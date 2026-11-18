"""Apply byte patches to copies of Anstoss 3 1.40 files (anstoss3.exe, D3D_Dll.dll).

Usage: python a3patch.py <original file> <output file> [patch-id ...]
The target is recognised by its SHA-256. Without patch ids all patches for that file are applied.
The original file is only read. Old bytes are checked at every patch site before writing.
"""
import hashlib
import sys

TARGETS = {
    # anstoss3.exe 1.40 (GOG)
    '89B88EF522574098014E9F1E68448593E2A992A8EBD0318760E552C3B15F6B2A': {
        'beste-mannschaft': [
            # Historisches/Beste Mannschaft: clear entry[19] instead of entry[20] when shifting (VA 0x007266FA)
            (0x003266FA, '66C74410260000', '66C744101C0000'),
        ],
        'versionsanzeige': [
            # Format string "%s Version 1.40/%s" (VA 0x00882378, used once at 0x004C5ADB to build a window caption
            # together with Simuversion() of the simulation DLL); the only "1.40" in the file. Shows the patch version.
            # Earlier patches wrote "1.41" ... "1.45" here (tools/patch_bauen.py accepts them as former states).
            (0x00482378, '25732056657273696F6E20312E34302F257300', '25732056657273696F6E20312E34362F257300'),
        ],
        'beste-mannschaft-anzeige': [
            # Screen Historisches/Beste Mannschaft (0x004665DD): rows = current year - start year, but from the 21st
            # season on the count is set to 19 instead of 20, so entry[19] (the season just finished) is never shown.
            # In the first 20 seasons entry[n-1] is the last finished season and is shown (checked on 97 savegames).
            # mov word ptr [ebp-0Eh],13h -> 14h (VA 0x004666DC). See docs/fehler-beste-mannschaft.md.
            (0x000666DC, '66C745F21300', '66C745F21400'),
        ],
        # The three patches below: see docs/befund-auf-abstiege.md (promotion/relegation counters, proven in code and
        # against 97 savegames on 15.11.2026). They only change what is counted at future season changes.
        'aufstieg-doppelt': [
            # 0x0069128A (one Regionalliga): the clubs going up are registered with the league's own index and with
            # statistics flag 1, although 0x006AE792.. already counted the same promotion with index 1.
            # Keep the list entry, drop the second count: push 1 -> push 0 (VA 0x0069137D).
            (0x0029137D, '6A01', '6A00'),
        ],
        'aufsteiger-liste': [
            # Same routine 0x0069128A: the two clubs going up from a Regionalliga are entered in the promotion list of
            # the league's own index (2 or 3), only so that 0x00680569 can leave them out of the new Regionalliga.
            # That list is the one shown as "Aufsteiger 3. Liga" and holds 4 clubs: it shows the two clubs that went up
            # to the 2nd league and only two of the real newcomers. The four clubs are already in list 1 (0x006AE792),
            # so enter (no-op, list full) and look up there: mov cx,[ebp+14h] / push ecx -> push 1 / nop x3, twice.
            (0x00291392, '668B4D1451', '6A01909090'),
            (0x00291438, '668B4D1451', '6A01909090'),
        ],
        'aufstieg-rl-sued': [
            # 0x00726382: league index 3 (Regionalliga Sued) has no column. Count index 2 and 3 in the third column,
            # as the relegation side already does: jne -> jl (VA 0x0072647F).
            (0x0032647C, '83F8027538', '83F8027C38'),
        ],
        'abstieg-spanien': [
            # 0x006B1F12 (Spain, league index 0): relegations are reported with league index 1 (block copied from the
            # German 2nd league). push 1 -> push 0 at VA 0x006B2042 and 0x006B208C.
            (0x002B2042, '6A018D95A0FC', '6A008D95A0FC'),
            (0x002B208C, '6A018D8DA0FC', '6A008D8DA0FC'),
        ],
        # The two patches below: see docs/befund-personal.md (retired players never become coaches).
        'trainer-nachwuchs': [
            # 0x0066DF9E puts a retiring player on the waiting list for coaches / goalkeeper coaches. It leaves at once
            # if 0x006FEB05 (pointer to the player's special name) returns non-zero, but that function never returns 0:
            # without a special name it returns the fixed address 0x01BE0B18. Both lists stayed empty in all savegames.
            # test eax,eax / je +5 / jmp end  ->  cmp eax,01BE0B18h / jne 0x0066DFC2 (existing jmp to the end) / nop nop
            (0x0026DFCF, '85C07405E997030000', '3D180BBE0175EC9090'),
        ],
        'trainer-geburt': [
            # 0x0066E374 takes a new coach from the waiting list (name, competence) but not his date of birth, so he
            # would keep the age of the man he replaces. The goalkeeper-coach routine copies it (0x0066E5AC).
            # The 64 bytes at VA 0x0066E3CA that copy the two name words are rewritten shorter, plus the date.
            (0x0026E3CA,
             '0FBF4DFC69C9D00200000FBF55FE6BD2248B4508668B8C117A0F8E0066894802'
             '0FBF55FC69D2D00200000FBF45FE6BC0248B4D08668B94027C0F8E0066895104',
             '0FBF4DFC'          # movsx ecx,word ptr [ebp-4]   land section
             '69C9D0020000'      # imul ecx,ecx,2D0h
             '0FBF55FE'          # movsx edx,word ptr [ebp-2]   list entry
             '6BD224'            # imul edx,edx,24h
             '8D8C117A0F8E00'    # lea ecx,[ecx+edx+008E0F7Ah]  -> entry
             '8B4508'            # mov eax,[ebp+8]              -> coach copy
             '668B11'            # mov dx,[ecx]                 first name
             '66895002'          # mov [eax+2],dx
             '668B5102'          # mov dx,[ecx+2]               last name
             '66895004'          # mov [eax+4],dx
             '8B5108'            # mov edx,[ecx+8]              date of birth (new)
             '89500A'            # mov [eax+0Ah],edx
             + '90' * 16),
        ],
        'trainer-ausgleich': [
            # Yearly balancing of coaches / managers per country (0x006B6000). If the average competence is below 6,
            # every tenth person is meant to gain 1-2 points: the code computes the gain, adds it to the sum and
            # touches the histogram, but never stores it in the person's value (the opposite branch for an average
            # above 10 does store, 0x006B61E3). The 180 bytes at VA 0x006B6057 are rewritten shorter with the store
            # added; esi is free here (saved by the function, used as scratch in the other branches).
            (0x002B6057,
             '0FBF55FC6BD2068B450C0FBF4C10028B5514668B044A662D01000FBF4DFC6BC9'
             '068B550C0FBF4C0A028B55146689044A6A02E882470D0083C4040FBFC083C001'
             '668945FE0FBF4DFC6BC9068B550C0FBF440A020FBF4DFE03C183F80F7E1A0FBF'
             '55FC6BD2068B450C0FBF4C1002BA0F0000002BD1668955FE0FBF45FE8B4D1003'
             'C8894D100FBF55FC6BD2068B450C0FBF4C10028B5514668B044A660501000FBF'
             '4DFC6BC9068B550C0FBF4C0A028B55146689044A',
             '0FBF75FC'          # movsx esi,word ptr [ebp-4]    index of the person
             '6BF606'            # imul esi,esi,6
             '03750C'            # add esi,[ebp+0Ch]             -> entry (number, value, other value)
             '0FBF4E02'          # movsx ecx,word ptr [esi+2]    value
             '8B5514'            # mov edx,[ebp+14h]             histogram
             '66FF0C4A'          # dec word ptr [edx+ecx*2]
             '6A02'              # push 2
             'E89D470D00'        # call 0078A810                 random 0..1
             '83C404'            # add esp,4
             '0FBFC0'            # movsx eax,ax
             '40'                # inc eax                       gain 1..2
             '0FBF4E02'          # movsx ecx,word ptr [esi+2]
             '8D1401'            # lea edx,[ecx+eax]
             '83FA0F'            # cmp edx,0Fh
             '7E07'              # jle +7
             'B80F000000'        # mov eax,0Fh
             '2BC1'              # sub eax,ecx                   gain = 15 - value
             '014510'            # add [ebp+10h],eax             sum
             '66014602'          # add word ptr [esi+2],ax       store the gain (was missing)
             '0FBF4E02'          # movsx ecx,word ptr [esi+2]
             '8B5514'            # mov edx,[ebp+14h]
             '66FF044A'          # inc word ptr [edx+ecx*2]
             'EB6A'              # jmp 006B610B (loop continue)
             + '90' * 106),
        ],
        'vereinsliste-spiele': [
            # Club list "most games" of a human manager (50 entries, docs/befund-vereinsstatistik.md): the flag "at the
            # club" (+8) is set when a player joins but never cleared for this list, so a full list never takes a new
            # player. The tail of the after-match routine 0x00744654 (VA 0x007447B1, 270 bytes: sort + store) is
            # rewritten shorter and first sets every flag from the current squad (club+0E2h count, +0B50h pointers).
            # New bytes come from tools/asm_vereinsliste.py (jump distances computed there).
            (0x003447B1,
             '0FBF4DDA85C90F840201000066C745D60000EB0C668B55D66683C201668955D6'
             '0FBF45D683F8310F8DCE000000668B4DD666894DF60FBF55D683C2016689957E'
             'FBFFFFEB12668B857EFBFFFF660501006689857EFBFFFF0FBF8D7EFBFFFF83F9'
             '327D320FBF55F66BD2160FBF84158AFBFFFF0FBF8D7EFBFFFF6BC9160FBF940D'
             '8AFBFFFF3BC27D0B668B857EFBFFFF668945F6EBB00FBF4DF685C97E590FBF55'
             'F66BD2168DB41580FBFFFFB9050000008D7DDCF3A566A50FBF45D66BC0168DB4'
             '0580FBFFFF0FBF4DF66BC9168DBC0D80FBFFFFB905000000F3A566A50FBF55D6'
             '6BD2168DBC1580FBFFFFB9050000008D75DCF3A566A5E919FFFFFF8D8580FBFF'
             'FF508B4D0851E8C8EAEEFF83C408',
             '66837DDA000F84030100008DBD80FBFFFF66833F00743766C7470800008B5508'
             '0FBF8AE20000008DB2500B000049781E8B048E668B10663B1775F2668B90CE00'
             '0000663B570675E566C74708010083C7168D45CC3BF872B98DBD80FBFFFF8BD7'
             '8D77168D45CC3BF07311668B420A663B460A7D028BD683C616EBE83BD7741AB9'
             '0B000000668B0766870266890783C70283C2024975EE83EF1683C7168D45B63B'
             'F872BB8D8580FBFFFF50FF7508E821EBEEFF83C408EB57' + '90' * 87),
        ],
        'trainer-reihenfolge': [
            # A title won by a human manager: 0x006B5497 enters it in the list and, at its end, writes the manager's row
            # of "Erfolgreichste Trainer" from the counters; only afterwards 0x006B583A increments the counter of that
            # title. The row therefore lags one title behind (docs/befund-trainer-eps.md). Both call sites: do the
            # increment first, then 0x006B5497 (which does not read the counters itself). Same bytes, calls re-based.
            (0x002B4EE1,
             '6A028B859CF7FFFF508D8DA8F7FFFF518B95A4F7FFFF52E89A05000083C410' '6A028D85A8F7FFFF50E82C09000083C408',
             '6A028D85A8F7FFFF50E84B09000083C408' '6A028B859CF7FFFF508D8DA8F7FFFF518B95A4F7FFFF52E88905000083C410'),
            (0x002B51DC,
             '668B450C508B4D08518D95A8F7FFFF528B85A4F7FFFF50E89F02000083C410' '668B4D0C518D95A8F7FFFF52E82E06000083C408',
             '668B4D0C518D95A8F7FFFF52E84D06000083C408' '668B450C508B4D08518D95A8F7FFFF528B85A4F7FFFF50E88B02000083C410'),
        ],
        'notenschnitt-details': [
            # Player details, page "Noten" (0x00561C46 ff.): the average divides the sum of the grade codes by ALL
            # appearances of the season, including those without a grade (code 0, e.g. late substitutes), so the
            # average comes out too good. The statistic "Notenschnitt Mannschaft" (0x0046E856) only counts graded
            # games. Patch: count the appearance only if the grade code (still in ecx) is >= 1.
            # See docs/befund-notenschnitt.md.
            (0x00161CD3,
             '668B85BEFDFFFF' '66050100' '668985BEFDFFFF',
             '83F901'                # cmp ecx,1                      carry if grade code = 0
             '66839DBEFDFFFFFF'      # sbb word ptr [ebp-242h],-1     counter + 1 - carry
             '90909090909090'),
        ],
        'verhasst-noten': [
            # Fan status "verhasst" (0x00770A72, called per squad player from 0x00770BAE): the average grade of the
            # last ten match days divides by all appearances, including those without a grade (code 0). Same error
            # as 'notenschnitt-details'; the user decided on 16.11.2026 that only graded games may count.
            # After "sar eax,2" eax holds the grade code: add it to the sum, count only if it is >= 1.
            (0x00370B2E,
             '0FBF55F4' '03D0' '668955F4' '668B45FE' '66050100' '668945FE',
             '660145F4'              # add word ptr [ebp-0Ch],ax      sum of grade codes
             '83F801'                # cmp eax,1                      carry if no grade
             '66835DFEFF'            # sbb word ptr [ebp-2],-1        graded games + 1 - carry
             '90909090909090909090'),
        ],
        'tagesform': [
            # League statistic "Tagesform" (class CTagesform; table built per club in 0x007230E1, page 0x0044EB33).
            # The value is the team's average grade of the last match (0x00705E9B = grade code of the last match, the
            # same value the game shows as IDC_EINZEL_NOTE_LETZTES) x 20; players without a grade are counted, and the
            # list is sorted descending, i.e. the worst team first. Decisions of the user (16.11.2026): graded
            # players only, best team first, show and name the value as an average grade.
            # The sorted list (0x006C5BAC) only takes an entry greater than an empty slot and keeps the greatest value
            # on top; reversing the compare function emptied the page (tested in the game). So the stored value is
            # 100 - grade x 10 and the page prints 100 - value as a grade with one decimal. All bytes come from
            # tools/asm_tagesform.py. See docs/befund-zaehler.md.
            (0x00323158, '7421', '74C2'),   # je 0072317B -> je 0072311C (loop head; frees 0x0072317B)
            # loop body: sum, count graded players, jump back; then the format string "%d.	%s	%d.%d" at 0x00723170
            (0x00323162,
             '0FBFC80FBF55EA03D1668955EA668B45EE66050100668945EEEB9F',
             '660145EA83F80166835DEEFFEBAC25642E0925730925642E256400'),
            # stored value = 100 - grade x 10, or 0 (not listed) without a graded player
            (0x0032317D,
             '0FBF4DEE85C97E140FBF45EA6BC00A0FBF4DEE99F7F9668945F8EB0666C745F80000',
             '0FBF4DEE85C97E140FBF45EA6BC00599F7F9F7D883C064EB0590909033C0668945F8'),
            # page row: place, club, grade with one decimal
            (0x0004ECB9,
             '0FBF853AFDFFFF0FBF8CC538FFFFFF510FBF953AFDFFFF668B84D536FFFFFF500FBF8D3AFDFFFF668B94CD34FFFFFF52E841F81E0083C408500FBF853AFDFFFF83C001506874A087008D8D3CFDFFFF51FF15B8D5800083C414',
             '0FBF853AFDFFFF8D94C534FFFFFF6A6458662B42049852996A0A59F7F9595250668B410250668B1152E848F81E0083C408500FBF853AFDFFFF405068703172008D8D3CFDFFFF51FF15B8D5800083C418909090909090909090'),
        ],
        'totalausfall': [
            # Newspaper headline 1519 "%1 erneut ein Totalausfall - %2: Wie lange müssen wir ihn noch ertragen?"
            # (0x005E5715 ff.: last grade >= 5.0, season average > 4.0, more than 10 appearances, club below its
            # target). The season average 0x00705EB6 reads the match-day bytes with the masks 0x80 / 0x1C instead of
            # 0xC0 / 0x3C (writer 0x006FF2F7) and scans all 46 slots; its result is at most 35, the headline needs
            # > 40 and can never appear. New body from tools/asm_totalausfall.py: match days played so far only,
            # correct masks, graded games only. Game logic - optional in the installer (user, 16.11.2026).
            # See docs/befund-notenschnitt.md.
            (0x00305EB6,
             '558BEC83EC10894DF066C745FE00008B45F00FBF0869C95403000081C15025C000894DF8C745F40000000066C745FC0000EB098B55F483C2018955F4837DF42E7D448B45F80345F433C98A881903000081E18000000085C9742A8B55F80355F433C08A821903000083E01CC1F8020FBF4DFE03C866894DFE668B55FC6683C201668955FCEBAD0FBF45FC85C07E150FBF45FE6BC00A0FBF4DFC99F7F9992BC2D1F8EB036633C08BE55DC3',
             '5657538BD98B450850E880C8F8FF83C4040FBFF883FF2E7E036A2E5F0FBF0369C05403000033D233F6EB180FB68C386928C000F6C1C0740BC1E90283E10F740303D1464F79E533C085F674086BC20A99F7FED1F85B5F5EC3CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'),
        ],
        'goldkettchen': [
            # Newspaper headline 1235 "Goldkettchen und teure Autos - %1 ein Prototyp des verzogenen Fußballmillionärs"
            # (random private-life event, 0x005FEBDF ff.). The average of the last three appearances (0x00705F60) has
            # the same mask error as 0x00705EB6 and no division by 2; the deduction of 2 from "Presse" handed to the
            # headline is never applied. Decision of the user (16.11.2026): correct it, optional in the installer, and
            # describe the effect in the patch notes. Both blocks come from tools/asm_goldkettchen.py:
            # routine = last three graded games of the current season, grade x 10 ("> 40" = worse than 4.0, my reading,
            # because the sister routine compares the same way); call site = headline + "Presse" - 2.
            # See docs/befund-notenschnitt.md.
            (0x00305F60,
             '558BEC83EC10894DF066C745FE00008B45F00FBF0869C95403000081C15025C000894DF8C745F42D00000066C745FC0000EB098B55F483EA018955F4837DF4007C528B45F80345F433C98A881903000081E18000000085C974388B55F80355F433C08A821903000083E01CC1F8020FBF4DFE03C866894DFE668B55FC6683C201668955FC0FBF45FC0FBF4D083BC17C02EB02EB9F0FBF55FC85D27E100FBF45FE6BC00A0FBF4DFC99F7F9EB036633C08BE55DC20400',
             '5657538BD98B450C50E8D6C7F8FF83C4040FBFF883FF2E7E036A2E5F0FBF0369C05403000033D233F6EB1D0FB68C386928C000F6C1C07410C1E90283E10F740803D14683FE037D034F79E033C085F674086BC20A99F7FED1F85B5F5EC3CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'),
            (0x001FEC04,
             '6A038B4D08E8527310000FBFD083FA287E236AFE6A008B4D08E82BFF0F005068000100006A0168D30400006A06E8FCAF180083C41866B80100EB04',
             '8B4D08E854731000663D28007E2D6AFE6A008B4D08E82FFF0F005068000100006A0168D30400006A06E800B0180083C4186AFE8B4D08E863231000'),
        ],
        'konto-anlagen': [
            # Confirmed in the game by the user on 16.11.2026, shipped with 1.44. See docs/befund-finanzen.md.
            # The club fortune carries every investment with the amount paid in; its growth is booked once, when it is
            # dissolved. The bank balance 0x0061FD97 subtracts the CURRENT value of the investments instead, so it is
            # too low by the whole growth while an investment runs and jumps by payout + growth when it is dissolved
            # ("double interest"). Both blocks come from tools/asm_konto.py.
            # 1) 0x0061FD97: subtract the amounts paid in (slot +0) of the active investments.
            (0x0021FD97,
             '558BEC5156578B450883C0188945FC8B4D088B81C0000000998B4D088B3103F08B790413FA8B55FC528B450850E8B8FEFFFF83C40803F013FA8B4D0851E86E8B020083C4042BF01BFA8B550852E8E18A020083C40403F013FA8BC68BD75F5E8BE55DC3',
             '5657538B5C24108B83C0000000998B338B7B0403F013FA8D43185053E8C9FEFFFF83C40803F013FA8D8BC80100006A0658F641130174052B311B790483C1184875EF53E8EB8A02005903C613D75B5F5EC3CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'),
            # 2) balance screen 0x004813AD, line "Aktuelles Vereinsvermögen": bank balance + investments at their
            #    current value - credits (was: fortune at season start + profit, i.e. without the growth).
            (0x00081426,
             '8B85E0FDFFFF8B88041400008B95E0FDFFFF8B82041400008B80C0000000998B3103F08B790413FA8B8DE0FDFFFF8B910414000083C218528B85E0FDFFFF8B880414000051E811E8190083C40803F013FA',
             '8B85E0FDFFFFFFB004140000E860E91900598BF08BFA8B85E0FDFFFFFFB004140000E8FA741C005903F013FA8B85E0FDFFFFFFB004140000E867741C00592BF01BFA909090909090909090909090909090'),
        ],
        'hochzeit-platzt': [
            # K01 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (not yet confirmed in the
            # game). See docs/befund-meldungen.md 6.14. Pre-routine 0x005FA5F8 of "Hochzeit platzt" (texts 1093, 1094)
            # collects the squad slots of the players with a wedding date in [ebp-48h] (count in [ebp-4Ch]) but then
            # indexes the squad list with the loop counter after the loop (= squad size), i.e. the slot behind the
            # last player. New: random 0..count-1 (0x0078A810) into the collected field, as the sister routine
            # 0x005F9FD0 does. "add esp,8" dropped (mov esp,ebp follows), "xor ax,ax" -> "xor eax,eax" to make room.
            (0x001FA687,
             '1D'                # (jle) 005FA6A5
             '0FBF45B6'          # movsx eax,word [ebp-4Ah]   loop counter = squad size
             '8B4D08'            # mov ecx,[ebp+8]
             '8B9481500B0000'    # mov edx,[ecx+eax*4+0B50h]
             '52'                # push edx
             '8B4508'            # mov eax,[ebp+8]
             '50'                # push eax
             'E8F4FCFFFF'        # call 005FA394
             '83C408'            # add esp,8
             'EB03'              # jmp 005FA6A8
             '6633C0',           # xor ax,ax
             '1E'                # (jle) 005FA6A6
             '52'                # push edx                   number of candidates
             'E882011900'        # call 0078A810              random 0..n-1
             '59'                # pop ecx
             '0FBF4445B8'        # movsx eax,word [ebp+eax*2-48h]   squad slot of the candidate
             '8B4D08'            # mov ecx,[ebp+8]
             'FFB481500B0000'    # push dword [ecx+eax*4+0B50h]     player pointer
             '51'                # push ecx
             'E8F0FCFFFF'        # call 005FA394
             'EB02'              # jmp 005FA6A8
             '33C0'),            # xor eax,eax
        ],
        'frauen-namen-1363': [
            # K02 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "rein optisch"; not
            # yet confirmed in the game). See docs/befund-meldungen.md 6.16. Text 1363 "%1 und %2 ... ihre Frauen %3
            # und %4" (case 2 of 0x005FEDB0, 0x005FF02E ff.) passed the buffer [ebp-118h], written only in case 1, as
            # %3 and 0 as %4. New: %3 / %4 = name of the wife (0x0070173F) of the first / second player; both are
            # married here (0x006FFB14 checked before). Room: two "push [ebp+x]" instead of mov + push, own
            # "mov ax,1 / jmp 005FFDB2" dropped - falls through into the identical return at 0x005FF072.
            (0x001FF03A,
             '6A00'              # push 0                     w
             '6A00'              # push 0                     %4
             '8D85E8FEFFFF50'    # lea eax,[ebp-118h] / push eax   %3 = buffer never written in this case
             '8D4D8451'          # lea ecx,[ebp-7Ch] / push ecx
             '8B4DF0'            # mov ecx,[ebp-10h]
             'E8FCFA0F00'        # call 006FEB4D              name of the second player
             '50'                # push eax                   %2
             '8B55F852'          # mov edx,[ebp-8] / push edx
             '6853050000'        # push 1363
             '6A60'              # push 60h
             '8B450850'          # mov eax,[ebp+8] / push eax
             'E800210000'        # call 00601166
             '83C420'            # add esp,20h
             '66B80100'          # mov ax,1
             'E9400D0000',       # jmp 005FFDB2
             '6A00'              # push 0                     w
             '8B4DF0'            # mov ecx,[ebp-10h]
             'E8FB261000'        # call 0070173F              wife of the second player
             '50'                # push eax                   %4
             '8B4DF8'            # mov ecx,[ebp-8]
             'E8F2261000'        # call 0070173F              wife of the first player
             '50'                # push eax                   %3
             '8D4D8451'          # lea ecx,[ebp-7Ch] / push ecx
             '8B4DF0'            # mov ecx,[ebp-10h]
             'E8F3FA0F00'        # call 006FEB4D              name of the second player
             '50'                # push eax                   %2
             'FF75F8'            # push dword [ebp-8]
             '6853050000'        # push 1363
             '6A60'              # push 60h
             'FF7508'            # push dword [ebp+8]
             'E8F9200000'        # call 00601166
             '83C420'            # add esp,20h
             '9090'),            # nop, nop -> 005FF072: mov ax,1 / jmp 005FFDB2
        ],
        'zeitung-1880': [
            # K03 of docs/korrekturliste-meldungen.md, version A, released by the user on 17.11.2026 (group "rein
            # optisch"; not confirmed in the game). See docs/befund-meldungen.md section 4. Newspaper headline 1880
            # (0x005F47A7) is called with flags 0x40000001 = "manager number and value for bit 0 follow", but only
            # the value -5 is passed: -5 is stored as manager number and 0x0078A0F5 then calls 0x006A426B(-5), outside
            # the manager tables. New flags 0x00000001: -5 is the value, no manager number, nothing is applied.
            # push 40000001h -> push 00000001h (VA 0x005F4799). Version B (pass the manager number, apply the -5):
            # see "Eventuell später" in the list.
            (0x001F4799, '6801000040', '6801000000'),
        ],
        'zeitung-1750': [
            # K04 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "rein optisch"; not
            # confirmed in the game). See docs/befund-meldungen.md section 4. Newspaper headline 1750 (0x0053CD00) is
            # called with flags 1 = "a value for bit 0 follows", but only the two names are passed; the value is read
            # from whatever lies on the stack (never applied: no manager number). New flags 0: no value is read.
            # push 1 -> push 0 (VA 0x0053CCF5).
            (0x0013CCF5, '6A016A0268D6060000', '6A006A0268D6060000'),
        ],
        # K05 and K06 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "Spiellogik,
        # kleine Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md 6.13. Table 0x0088DC58 of the
        # simple money events (0x005E9A4F), 108 pairs text / value (int32 each): negative = booked as expense,
        # positive = as income, the text shows the amount without sign. Each site covers the whole pair.
        'geld-690': [
            # index 91, text 690 "... Sie sparen %s ein": -120 -> +120 (was booked as an expense of 12 000)
            (0x0048DF30, 'B2020000' '88FFFFFF', 'B2020000' '78000000'),
        ],
        'geld-697': [
            # index 98, text 697 "... Kostenpunkt: %s": +80 -> -80 (was booked as income of 8 000)
            (0x0048DF68, 'B9020000' '50000000', 'B9020000' 'B0FFFFFF'),
        ],
        'verhandlung-224': [
            # K07 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "Spiellogik, kleine
            # Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md 6.13. Question 224 offers %4 as
            # additional win bonuses and "maybe %5" (= 2 x %4, 0x005E89B1) after a successful negotiation; on success
            # (text 225) only the single amount was added to club +0x2F8, the same as without negotiating.
            (0x001E89F7,
             '8B5508'            # mov edx,[ebp+8]
             '8B82F8020000'      # mov eax,[edx+2F8h]
             '0385B4F2FFFF'      # add eax,[ebp-0D4Ch]        single amount
             '8B4D08'            # mov ecx,[ebp+8]
             '8981F8020000'      # mov [ecx+2F8h],eax
             'EB14',             # jmp 005E8A25
             '8B5508'            # mov edx,[ebp+8]
             '8B85B4F2FFFF'      # mov eax,[ebp-0D4Ch]        single amount
             'D1E0'              # shl eax,1                  doubled, as in 0x005E89B7
             '0182F8020000'      # add [edx+2F8h],eax
             '90909090909090'    # 7 x nop
             'EB14'),            # jmp 005E8A25
        ],
        'randale-284': [
            # K08 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "rein optisch"; not
            # confirmed in the game). See docs/befund-meldungen.md 6.13. Riots after a home match, unfavourable branch
            # (0x005EA167 ff.): 100 000 are booked as expense, but the second text was 283 ("quickly under control")
            # instead of 284 ("sued for more than %s ... settle for %s"). Both amounts come from 0x004DAF8F, which
            # always writes to the same buffer 0x008EC88C: the settlement amount is now copied (strcpy 0x007E0FFE) to
            # [ebp-60h] first - the unused tail of the 504-byte buffer [ebp-218h] that only holds text 282 here; no
            # other access in the routine. Stack is not cleaned after strcpy (ebp frame, epilogue mov esp,ebp).
            (0x001EA186,
             'A17CB3A300'        # mov eax,[00A3B37Ch]        settlement = 100 x unit
             '8985CCFBFFFF'      # mov [ebp-434h],eax
             '8B8DCCFBFFFF51'    # mov ecx,[ebp-434h] / push ecx
             'E8F20DEFFF'        # call 004DAF8F              amount as text -> 0x008EC88C
             '83C40450'          # add esp,4 / push eax
             '8B1548B3A30052'    # mov edx,[00A3B348h] / push edx   claim = 500 x unit
             'E8E20DEFFF'        # call 004DAF8F              same buffer again
             '83C40450'          # add esp,4 / push eax
             '681B010000',       # push 283
             'A17CB3A300'        # mov eax,[00A3B37Ch]
             '8985CCFBFFFF'      # mov [ebp-434h],eax         (booked later at 0x005EA1FB)
             '50'                # push eax
             'E8F80DEFFF'        # call 004DAF8F
             '59'                # pop ecx
             '50'                # push eax                   source
             '8D4DA0'            # lea ecx,[ebp-60h]
             '51'                # push ecx                   destination
             'E85C6E1F00'        # call 007E0FFE              strcpy, returns the destination
             '50'                # push eax                   second %s = settlement (copy)
             'FF3548B3A300'      # push dword [00A3B348h]
             'E8E10DEFFF'        # call 004DAF8F
             '59'                # pop ecx
             '50'                # push eax                   first %s = claim
             '681C010000'        # push 284
             '90'),              # nop
        ],
        'straf-frage-stufe1': [
            # K09 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "Spiellogik, kleine
            # Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md 6.2. Penalty question 0x005F29BC,
            # level 1 (0x005F2C3C-0x005F2C92), answers 1566 "1 Spiel interne Sperre" / 1567 "%4 Strafe" / 1568 "Nicht
            # so schlimm". Old: answer 0 = -10 without ban, answer 1 = -2 without money, answer 2 = fine booked.
            # New, values taken from level 2 (0x005F2CCD ff., decision of the user): answer 0 = ban of 1 match
            # (0x0070302D), -3 on the trainer part of the motivation (0x007007A1), counter 0x007049CC; answer 1 = fine
            # [0x00A3B3CC] (the amount shown as %4, 0x005F2A1F) on club +0x28C; answer 2 = nothing.
            (0x001F2C3C,
             '0FBF0DEE21A300' '85C9' '7514'              # answer 0 ?
             '6AF6' '8B4D14' 'E850DB1000'                # -10
             '8B4D14' 'E8731D1100' 'EB38'                # counter
             '0FBF15EE21A300' '83FA01' '7514'            # answer 1 ?
             '6AFE' '8B4D14' 'E830DB1000'                # -2
             '8B4D14' 'E8531D1100' 'EB18'                # counter
             '8B450C' '8B888C020000' '030DCCB3A300'      # answer 2: fine
             '8B550C' '898A8C020000',
             '0FBF0DEE21A300'    # movsx ecx,word [00A321EEh]   answer
             '85C9'              # test ecx,ecx
             '751E'              # jne 005F2C65
             '6A01'              # push 1
             '8B4D14'            # mov ecx,[ebp+14h]
             'E8DC031100'        # call 0070302D              ban: 1 match
             '6AFD'              # push -3
             '8B4D14'            # mov ecx,[ebp+14h]
             'E846DB1000'        # call 007007A1
             '8B4D14'            # mov ecx,[ebp+14h]
             'E8691D1100'        # call 007049CC
             'EB2E'              # jmp 005F2C93
             '49'                # dec ecx
             '752B'              # jne 005F2C93               answer 2: nothing
             '8B450C'            # mov eax,[ebp+0Ch]
             '8B0DCCB3A300'      # mov ecx,[00A3B3CCh]
             '01888C020000'      # add [eax+28Ch],ecx         answer 1: fine
             + '90' * 28),
        ],
        'streit-liste': [
            # K10 of docs/korrekturliste-meldungen.md, released by the user on 17.11.2026 (group "Spiellogik, kleine
            # Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md 6.1. 0x00703930 removes a player
            # from the second list of three (static record +0x1FE, quarrels) and wrote the closing 0 into the first
            # list (+0x1F8, friends): mov word [eax+edx*2+1F8h],0 -> ...+1FEh (VA 0x007039D0), as the sister routine
            # 0x00703854 does for its own list.
            (0x003039D0, '66C78450F80100000000', '66C78450FE0100000000'),
        ],
        'jugend-abwerben-vertrag': [
            # Correction of 18.11.2026 (docs/befund-personal.md, "Jugendvertrag"), confirmed in the game by the user,
            # shipped with 1.46 (group "Berechnungskorrekturen"). The manager's screen "Jugendspieler ohne Vertrag"
            # (0x004D7038, branch 0x004D766E) writes the salary (+0x88) of a youth player taken from another club
            # but not the 10 contract years (+0x94) that the two sister paths set right after the salary
            # (0x004D8DA9, 0x006C3D7F). ecx still holds the player (loaded at 0x004D778D). The 15 bytes that called
            # the cdecl wrapper 0x00707BD4 (mov edx,[ebp-0C88h]; push edx; call; add esp,4) become:
            # mov byte [ecx+94h],0Ah; call 0x0070429C (thiscall, no stack arguments, what the wrapper called); 3 nop.
            (0x000D779A, '8B9578F3FFFF52E82E04230083C404', 'C681940000000AE8F6CA2200909090'),
        ],
        'maulwurf-zaehler': [
            # K11 of docs/korrekturliste-meldungen.md, simple version, released by the user on 17.11.2026 (group
            # "Spiellogik, kleine Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md section 5.
            # 0x0069FE73 raises the counter of the "Maulwurf" affair (club +0xDF8, bits 18-20 = 0..7) and limits it
            # to 15: 7 + 1 became 0 and the series of headlines 1703-1706 could start again in the same season.
            # New limit 7: cmp [ebp-4],0Fh / mov [ebp-4],0Fh -> 7 (VA 0x0069FE9D). Clearing bit 21 at the end of the
            # routine is intended (bit 21 = "headline for this level already issued", 0x005E5650 / 0x005E536D) and
            # stays. Widening the counter to 4 bits (levels 8 and 10, texts 1707 / 1708): "Eventuell später" K11-B.
            (0x0029FE9D, '837DFC0F' '7E07' 'C745FC0F000000', '837DFC07' '7E07' 'C745FC07000000'),
        ],
        # K12 of docs/korrekturliste-meldungen.md, all seven released by the user on 17.11.2026 (group "Spiellogik,
        # kleine Auswirkung"; not confirmed in the game). See docs/befund-meldungen.md section 4. Seven headlines pass a
        # deduction for the "Presse" part of the player's motivation without a player number, so it was never applied;
        # the sister headlines apply it themselves right after the call (0x00700FA2). The blocks come from
        # tools/asm_presse.py (how the 10 bytes for the extra call are gained is described there).
        'presse-1125': [
            # headline 1125 "Frau von %1 bei Bankueberfall erwischt": "Presse" -3 applied to the player (VA 0x005FB53A)
            (0x001FB53A,
             '83C41C8B4D0CE8AC5C10006689458E6A008B4D0CE8BD5C1000668945FE6A006AFB8B4D0CE8AD5C100050668B55FE526A036AFB8B4D0CE8645B100050668B458E506A028B4D0CE8BA611000508B4D0C5168640400006A608B550852E86460000083C430',
             '6AFD8B4D0CE85E5A10008B4D0CE8A55C10006689458E6A008B4D0CE8B65C1000668945FE6A006AFB8B4D0CE8A65C100050668B55FE526A036AFB8B4D0CE85D5B100050FF758E6A028B4D0CE8B561100050FF750C68640400006A60FF7508E861600000'),
        ],
        'presse-1188': [
            # headline 1188 "Schoenheitsoperation bei %1": "Presse" -4 applied to the player (VA 0x005FDF3D)
            (0x001FDF3D,
             '0FBFD083FA0A7E5E8B450C50E8BC7F170083C4040FBFC883F9027E4A8B4D0CE81AB5090085C0743E6AFC6A008B4D08E8DC0B10005068000100006A0168A40400006A06E8ADBC180083C4186A006A008B55085268A30400006A608B450C50E88F2F000083C418',
             '6683F80A7E60FF750CE8BF7F17006683F8027E528B4D0CE822B5090085C074466AFC6A008B4D08E8E40B10005068000100006A0168A40400006A06E8B5BC18006AFC8B4D08E81B3010006A006A008B55085268A30400006A608B450C50E8902F000083C41890'),
        ],
        'presse-1197': [
            # headline 1197 "%1 steht vor dem Nichts": "Presse" -3 applied to the player (VA 0x005FE0EE)
            (0x001FE0EE,
             '83C41C8B4D08E82F321000668945966A006AF68B4D08E80731100050668B4D96516A036A008B55085268AC0400006A608B450C50E81C2F000083C424',
             '6AFD8B4D08E8AA2E10008B4D08E828321000668945966A006AF68B4D08E80031100050FF75966A036A00FF750868AC0400006A60FF750CE8192F0000'),
        ],
        'presse-1201': [
            # headline 1201 "%1 geht lieber Golfen": "Presse" -2 applied to the player (VA 0x005FE23E)
            (0x001FE23E,
             '8B450C50E8FD44090083C4040FBFC883F90A7E468B550833C08A425485C0753A6A138B4D0C518D559852E8D74C130083C40C6AFE68E226A3006A008B4D08E8CC0810005068000100006A0268B10400006A05E89DB9180083C41C',
             'FF750CE8FE4409006683F80A7E4C8B550833C08A425485C075406A138B4D0C518D559852E8DD4C13006AFE68E226A3006A008B4D08E8D50810005068000100006A0268B10400006A05E8A6B918006AFE8B4D08E80C2D10009090'),
        ],
        'presse-1269': [
            # headline 1269 "%1 poebelt friedliche Passanten an": "Presse" -4 applied to the player (VA 0x005E0F0D)
            (0x001E0F0D,
             '0FBFC085C0754F6AFC8B4D0883C10A516A008B4D10E826DC11005068000100006A0268F50400006A07E8F78C1A0083C41C6A028B4D10E84D1E12006A028B55105268F40400008B450C508B4D0851E85C1A010083C414',
             '6685C075516AFC8B4D0883C10A516A008B4D10E828DC11005068000100006A0268F50400006A07E8F98C1A006AFC8B4D10E85F0012006A028B4D10E8481E12006A02FF751068F4040000FF750CFF7508E85A1A010090'),
        ],
        'presse-1528': [
            # headline 1528 "%1 mit schweren Vorwuerfen gegen den Trainer": "Presse" -4 applied to the player (VA 0x005E5BDD)
            (0x001E5BDD,
             '0FBFC883F9507D4A6AFC8B550883C20A526A008B4D10E8558F11005068000100006A0268F80500006A08E826401A0083C41C6A008B450883C00A508B4D105168F70500006A608B550C52E803B3010083C418',
             '6683F8507D4C6AFC8B550883C20A526A008B4D10E8578F11005068000100006A0268F80500006A08E828401A006AFC8B4D10E88EB311006A008B450883C00A50FF751068F70500006A60FF750CE800B30100'),
        ],
        'presse-1530': [
            # headline 1530 "%1 kritisiert Trainer %2": "Presse" -4 applied to the player (VA 0x005E5D03)
            (0x001E5D03,
             '0FBFC883F9507D4A6AFC8B550883C20A526A008B4D10E82F8E11005068000100006A0268FA0500006A08E8003F1A0083C41C6A008B450883C00A508B4D105168F90500006A608B550C52E8DDB1010083C418',
             '6683F8507D4C6AFC8B550883C20A526A008B4D10E8318E11005068000100006A0268FA0500006A08E8023F1A006AFC8B4D10E868B211006A008B450883C00A50FF751068F90500006A60FF750CE8DAB10100'),
        ],
        'presse-nutzen-vertrauen': [
            # K13 of docs/korrekturliste-meldungen.md (worked through alone, to be reviewed). See docs/befund-meldungen.md section 4.
            # "Presse nutzen" (dialog routine 0x005378D6, once per season): choices 1 / 2 create the headlines 1743 / 1744 and pass the
            # manager number and +5 / -10 for bit 3 (manager +0x9C = base of "Vertrauen", 0x007701B2), but with flags 8 instead of
            # 0x40000008, so the number was read as the value and nothing was applied. push 8 -> push 40000008h; the 3 bytes come
            # from the dropped add esp,1Ch (the routine ends with mov esp,ebp). Choice 3 of the same routine passes its flags correctly.
            (0x00137AD2,
             '6A086A0168CF0600006A06E85021250083C41C',
             '68080000406A0168CF0600006A06E84D212500'),
            (0x00137B0A,
             '6A086A0168D00600006A07E81821250083C41C',
             '68080000406A0168D00600006A07E815212500'),
        ],
        'trennung-1083': [
            # K15 (worked through alone, to be reviewed): text 1083 "... Es kommt zur Trennung." did not end the relationship.
            # New: 0x00702467 as at the sister text 1079 (0x005F9816). Block from tools/asm_nacht.py.
            # Corrected 18.11.2026: the 'push 0' (w4 of the message) now follows the random call; before, the argument
            # left on the stack by the dropped 'add esp,4' was taken as w4 (10 instead of 0).
            (0x001F9F76,
             '6A006A0AE89108190083C4040FBFC8BAF6FFFFFF2BD1528B4D0CE84471100050668B45FC506A028B4D0CE89A771000508B4D0C51683B0400006A608B550852E88970000083C424',
             '8B4D0CE8E98410006A0AE88B0819000FBFC8BAF6FFFFFF2BD16A00528B4D0CE83F71100050FF75FC6A028B4D0CE8B478100050FF750C683B0400006A60FF7508E8887000009090'),
        ],
        'hochzeit-absage-1093': [
            # K14 (worked through alone, to be reviewed): text 1093 "... muss seine Hochzeit absagen ... Die beiden Frauen wollen
            # nichts mehr von ihm wissen." (0x005FA394 case 1, player [ebp+0Ch]) tried to remove the wedding date from the list
            # 0x008EB8B0 with 0x004377B7(number, &[ebp-8]), but [ebp-8] is never written: the date stayed and the wedding took place
            # (0x005FD386 -> 0x00702B15). New: 0x00702467 (end the relationship), which removes the date with the stored key, clears
            # it and sets the status to "no relationship" - the routine the sister text 1079 uses. 11 nop.
            (0x001FA464,
             '8D4DF8518B550C668B0250E843D3E3FF83C408',
             '8B4D0CE8FB7F10009090909090909090909090'),
        ],
        'freundin-ausgespannt-1104': [
            # K16 (worked through alone, to be reviewed): text 1104 "Ihr Spieler %1 hat Ihrem Spieler %2 die Freundin ausgespannt"
            # (0x005FAB7E ff.): the second player q ([ebp-8]) takes over the partner of the chosen player p ([ebp+0Ch]) (0x00702668),
            # but the message named p as %1 and q as %2. New: %1 = q, %2 = p; the before/after value shown is now q's (both players
            # get +3 as before). Five operands [ebp-8] <-> [ebp+0Ch] swapped between 0x005FABF9 and 0x005FAC31.
            (0x001FABF9,
             '6A038B4DF8E8D66410008B4D0CE8E6651000668945FC6A006A038B4D0CE8BE64100050668B55FC526A026A008B4DF8E8203F1000508B450C',
             '6A038B4D0CE8D66410008B4DF8E8E6651000668945FC6A006A038B4DF8E8BE64100050668B55FC526A026A008B4D0CE8203F1000508B45F8'),
        ],
        'ex-freundin-1109-1110': [
            # K17 (worked through alone, to be reviewed): effects of the texts 1109 and 1110 were exchanged. 1109 now only sets its
            # marker (bit 25), 1110 goes back to the former partner (0x00702762, which now also sets the status "Freundin").
            # Blocks from tools/asm_nacht.py (ex-1109, ex-1110, ex-702762).
            (0x001FAE76,
             '8B4D0CE8E47810006A006A008B4D0CE8D2691000508B4D0CE8AC681000508B4D0C5168550400006A608B550852E8BE62000083C420',
             '6A018B4D0CE8797A10006A006A008B4D0CE8D0691000508B4D0CE8AA681000508B4D0C5168550400006A608B550852E8BC62000090'),
            (0x001FAEDB,
             '8B4D0CE82F7D100025FF00000085C0752D6A006A008B4D0CE864691000508B4D0CE83E681000508B450C5068560400006A608B4D0851E85062000083C420',
             '8B4D0CE82F7D100084C075326A006A008B4D0CE869691000508B4D0CE84368100050FF750C68560400006A60FF7508E8576200008B4D0CE84B7810009090'),
            (0x00302762,
             '558BEC83EC0C894DF48B45F40FBF0869C9540300008A91D527C0008855FB8B45F40FBF0869C9540300008A91D727C0008855FA8B45F40FBF0869C9540300008B91DC26C0008955FC8B4DF4E8B5FCFFFF8B45F40FBF0869C9540300008A55FB8891D327C0008B45F40FBF0869C9540300008A55FA8891D627C0008B45F40FBF0869C9540300008B55FC8991D826C0008B45F40FBF0869C95403000081C1C026C000518B55F4668B0250E8A74FD3FF83C4088B4DF40FBF1169D254030000C682C026C000008BE55DC3',
             '558BEC83EC0C894DF40FBF0169C0540300008A90D527C0008855FB8A90D727C0008855FA8B90DC26C0008955FCE8D3FCFFFF8B4DF40FBF0169C0540300008A55FB8890D327C0008A55FA8890D627C0008B55FC8990D826C00005C026C000500FBF1152E8ED4FD3FF83C4088B4DF40FBF0169C054030000C680C026C000006A01E8C90300008BE55DC3909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090'),
        ],
        'freund-klagt-1365': [
            # K19 (worked through alone, to be reviewed): text 1365 "%1 ... erzählt ihm, was ihm ... stinkt. %2 muss ihm ... recht geben"
            # (0x005FF120 ff.). A = [ebp-8] is the friend with the higher satisfaction (> 100), B = [ebp-10h] the lower one (< 85);
            # B.0x00705539(A) raises B's two lowest motivation parts and lowers A's by the same amount, so B is the one who complains.
            # The message named A as %1 and B as %2. New: player = B, second name = A (two operands exchanged).
            (0x001FF1B9,
             '8B4DF0E88CF90F00508B4DF851',
             '8B4DF8E88CF90F00508B4DF051'),
        ],
        'autobiographie-1172': [
            # K20 (worked through alone, to be reviewed): text 1172 (autobiography): the quarrel was entered between the two
            # team-mates named in the message instead of between each of them and the author. Block from tools/asm_nacht.py.
            (0x001FDB07,
             '8B5508528B450C50E8C4EEFEFF83C4088945908B4D08518B550C52E8B1EEFEFF83C40889458C837D90007406837D8C007502EB6E8B45903B458C7502EB648B4D8C518B4D90E8A36210006A006A008D9558FFFFFF528B4D8CE8E90F1000508D8524FFFFFF508B4D90E8D90F1000508B4D085168940400006A608B550C52E8DD35000083C420',
             'FF7508FF750CE8C6EEFEFF894590FF7508FF750CE8B8EEFEFF89458C837D90007406837D8C007502EB788B45903B458C7502EB6EFF75908B4D08E8AE621000FF758C8B4D08E8A36210006A006A008D9558FFFFFF528B4D8CE8E90F1000508D8524FFFFFF508B4D90E8D90F100050FF750868940400006A60FF750CE8DF35000083C4209090'),
        ],
        'dauer-1193': [
            # K21 (worked through alone, to be reviewed): text 1193 (spade in the foot, "fällt drei Wochen aus"):
            # 0x00766B92(player, kind 37, -1) took the default of kind 37 = 112 days (table 0x008AC340). New duration 21:
            # push -1 -> push 15h (third argument = duration in days).
            (0x001FDFDF,
             '6AFF6A25',
             '6A156A25'),
        ],
        'dauer-1215': [
            # K22 (worked through alone, to be reviewed): text 1215 (sprained hand, "die nächsten drei Wochen"): kind 90 has
            # the default 7 days. New duration 21: push -1 -> push 15h.
            (0x001FE61E,
             '6AFF6A5A',
             '6A156A5A'),
        ],
        'dauer-1076': [
            # K25 (worked through alone, to be reviewed): text 1076 (torn ligament, "fällt vier Wochen aus"): kind 10 has
            # the default 35 days. New duration 28: push -1 -> push 1Ch.
            (0x001F974F,
             '6AFF6A0A',
             '6A1C6A0A'),
        ],
        'frische-1180': [
            # K28 (worked through alone, to be reviewed): text 1180 announces the loss of one freshness point, nothing was applied.
            # New: 0x005E5F40(-1) as text 1329 does with -5. Block from tools/asm_nacht.py.
            (0x001FDD89,
             '6A02E880CA180083C4048985FCFEFFFF83BDFCFEFFFF00740B83BDFCFEFFFF01741FEB536A006A008B550852689C0400006A608B450C50E86A31000083C418EB36',
             '6A02E880CA18008985FCFEFFFF85C075306AFF8B4D08E89C81FEFF6A006A00FF7508689C0400006A60FF750CE875310000EB449090909090909090909090909090'),
        ],
        'rueckgabe-1982': [
            # K34 (worked through alone, to be reviewed): after message 1982 (no Christmas present) the case of 0x005FB264 ran
            # into the shared "xor ax,ax" at 0x005FB601 and returned 0 = nothing happened. New: jump to the existing
            # "mov ax,1 / jmp 005FB604" at 0x005FB59D instead of the add esp,24h (the routine ends with mov esp,ebp).
            (0x001FB5FE,
             '83C424',
             'EB9D90'),
        ],
        'name-fruehere-partnerin': [
            # K37 (worked through alone, to be reviewed): 0x0070185C (name of the former partner) read the name index from
            # savegame 0x265 but the name group from 0x266 (group of the present partner) instead of 0x267, where 0x00702467
            # stores the group of the former partner. movzx dx,byte [ecx+00C027D6h] -> ...D7h (VA 0x00701884).
            (0x00301884,
             '660FB691D627C000',
             '660FB691D727C000'),
        ],
        'art-1312': [
            # K44 (worked through alone, to be reviewed): message 1312 changes and shows savegame 0x274 ("Ablenkung", 0x00701328 /
            # 0x00701210) but passed kind 1 = "Mannschaft" for the label (table 0x008808B0). New kind 3: push 1 -> push 3.
            (0x001E19C9,
             '6A016A008B4510',
             '6A036A008B4510'),
        ],
        'art-1116-1117': [
            # K45 (worked through alone, to be reviewed): messages 1116 / 1117 (mother-in-law) read and change savegame 0x274
            # ("Ablenkung", 0x00701210) but passed kind 2 = "Privates". New kind 3 at both sites: push 2 -> push 3.
            (0x001FB3AE,
             '6A026A008B4D0C',
             '6A036A008B4D0C'),
            (0x001FB406,
             '6A026A008B4D0C',
             '6A036A008B4D0C'),
        ],
        'art-1168': [
            # K46 (worked through alone, to be reviewed): message 1168 (diary, "Die Stimmung in der Mannschaft sinkt") changes club
            # +0x9E (0x00698EF6) and passed kind 10 = "Beliebtheit Öffentlichkeit". New kind 11 = "Stimmung": push 0Ah -> push 0Bh.
            (0x001FDA33,
             '6A0A6A008B4D08',
             '6A0B6A008B4D08'),
        ],
        'text-1389': [
            # K47 (worked through alone, to be reviewed): case 28 of 0x005FEDB0 (two players of the same position, quarrel entered)
            # showed text 1388 ("... haben sich beide in %3, die Schwester ... verliebt") instead of 1389 ("... die die gleiche
            # Position spielen, verstehen sich privat nicht besonders gut"), which has no other site. push 56Ch -> push 56Dh.
            (0x001FF98E,
             '686C050000',
             '686D050000'),
        ],
        'spitzel-983': [
            # K33 (worked through alone, to be reviewed): after message 983 the exposed spy kept the spy bit 0x8000 and was drawn
            # again. New: 0x0070020F(0). Block from tools/asm_nacht.py.
            (0x001E4F10,
             '66C745F60000EB0C668B45F666050100668945F60FBF4DF68B55080FBF82E20000003BC87D176AF60FBF4DF68B55088B8C8A500B0000E856B81100EBCB6A018B4D0CE8C8B311006A008B4D0CE86EBC11006A006A008B450C5068D70300006A608B4D0851E8B6BF010083C418',
             '66C745F60000EB0466FF45F68B55080FBF4DF6663B8AE20000007D106AF68B8C8A500B0000E867B81100EBDC6A018B4D0CE8D9B311006A008B4D0CE87FBC11006A008B4D0CE8B5B211006A006A00FF750C68D70300006A60FF7508E8BFBF0100909090909090909090909090'),
        ],
        'frau-1176-1177': [
            # K40, part (worked through alone, to be reviewed): texts 1176 / 1177 got 0 as name of the wife (%2).
            # New: name of the partner (0x0070173F); both branches merged. Block from tools/asm_nacht.py.
            (0x001FDC9C,
             '8B4D08E8E62010000FBFC085C0751D6A006A008B4D085168980400006A608B550C52E86C32000083C418EB1B6A006A008B45085068990400006A608B4D0C51E84F32000083C418',
             '6A008B4D08E8993A100050FF75088B4D08E8D82010006685C00F95C00FB6C00598040000506A60FF750CE864320000909090909090909090909090909090909090909090909090'),
        ],
        'name-geliebte-1094': [
            # K41, part (worked through alone, to be reviewed): text 1094 "... die Telefonnummer seiner anderen Freundin %3"
            # (0x005FA394 case 2). 0x0070282A makes the lover the partner and clears her index (savegame 0x264) BEFORE the
            # names are read, so 0x007017DB returned the name with index 0. New: 0x0070173F (name of the partner = the former
            # lover; same name group byte). call 007017DB -> call 0070173F (VA 0x005FA51F). The order of %1 / %2 in the text
            # ("%1, die Freundin von %2" with %1 always = player name) can only be corrected in the text file.
            (0x001FA51C,
             '8B4D0CE8B7721000',
             '8B4D0CE81B721000'),
        ],
        'frau-969': [
            # K40, part (worked through alone, to be reviewed): text 969 got 0 as name of the wife (%2). New: 0x0070173F.
            # Block from tools/asm_nacht.py.
            (0x001E4D17,
             '6A006A008B550C5268C90300006A608B450850E800C2010083C418',
             '6A008B4D0CE81ECA110050FF750C68C9030000EBCB909090909090'),
        ],
        'frau-weg-1115': [
            # K18 (released 18.11.2026): text 1115 (wife leaves with the child, 'verliert einen Punkt seiner Spielstärke') required strength == 1
            # and only lowered savegame 0x273. New: strength > 1 as at the sister texts 1163 / 367, strength - 1, 0x00702467 (end the
            # relationship). Block from tools/asm_nacht.py. The text contains '%s' and must be corrected together with this (K39).
            (0x001FB2F5,
             '8B4D0C33D28A510283FA01756F8B4D0CE80A48100085C074638B4D0CE8744A10000FBFC083F80175538B4D0CE8CB5E10006689458E6A006A0BE8DDF4180083C4040FBFC8BAD8FFFFFF2BD1528B4D0CE8905D100050668B458E506A028B4D0CE803651000508B4D0C51685B0400006A608B550852E8D55C000083C424',
             '8B4D0C807902017E73E81148100085C0746A8B4D0CE87B4A10006683F801755C8B4D0CE8D45E10006689458E8B4D0CFE4902E83B7110006A0BE8DDF418000FBFC8BAD8FFFFFF2BD16A00528B4D0CE8915D100050FF758E6A028B4D0CE80665100050FF750C685B0400006A60FF7508E8DA5C00009090909090909090'),
        ],
        'verletzung-92-93': [
            # K23 / K24 (released 18.11.2026): the injury kinds 92 ('Stickstoffvergiftung', text 1225) and 93 ('Autounfall', text 1227)
            # have names (table 0x008A8758 -> 3990 / 3991) but empty rows in the kind table 0x008AC340 (10 bytes per kind; rows 70-91
            # all read 00 dd 02 00 07 00 ..., dd = days), so 0x00766B92(player, kind, -1) entered an injury of 0 days. New: rows 92
            # and 93 filled like their neighbours 90 / 91 with 7 and 14 days (data, file offsets 0x4AC6D8 and 0x4AC6E2).
            (0x004AC6D8,
             '0000000000',
             '0007020007'),
            (0x004AC6E2,
             '0000000000',
             '000E020007'),
        ],
        'fuehrerschein': [
            # K31 / K30 (released 18.11.2026): the driving-licence byte (savegame 0x26E) held 'months left' and was never counted down,
            # so a licence once withdrawn never came back. New: 0x00702D31 stores the month of expiry ((year * 12 + month + v) & 0xFF)
            # and every read clears it once it has passed; the reader 0x00702D6F moves to 0x00702D7B (two calls redirected). Block
            # from tools/asm_nacht.py. Last site = K30: text 1217 'für einen Monat' stored 2, now 1.
            (0x00302D31,
             '558BEC51894DFC0FBF450885C07C158B4DFC0FBF1169D2540300008A45088882DE27C0008B4DFC0FBF1169D254030000660FB682DE27C0008BE55DC20400558BEC51894DFC8B45FC0FBF0869C95403000033D28A91DE27C0008BC2F7D81BC0408BE55DC3',
             '0FBF0169C0540300008D88DE27C0000FB715DECBB5006BD20C0215DCCBB5008B4424046685C07809740500D075014088010FB60185C0740F28D03C077608C6010033C0C2040040C204006AFFE8AFFFFFFFF7D81BC040C390909090909090909090909090'),
            (0x001FE9B4,
             'E8B6431000',
             'E8C2431000'),
            (0x001FEB2E,
             'E83C421000',
             'E848421000'),
            (0x001FE6A5,
             '6A028B4D08E882461000',
             '6A018B4D08E882461000'),
        ],
        'schueler-merker': [
            # K38 / K32 (released 18.11.2026): the pupil marker (bits 3-4 of savegame 0x260; 0x007064C9, 0x007064F6, 0x00706523,
            # 0x0070654A) shared bit 4 with the group-leader flag (0x007006C4 / 0x007006E8). New: the pupil marker lives in bits 5-6,
            # which no routine uses (five sites: shift counts 3 -> 5, clear mask E7 -> 9F). Last site = K32: text 1565 (Abitur) now
            # sets the marker 3 'school finished' that the pre-routine tests (0x005F9DD0). Block from tools/asm_nacht.py.
            (0x003064E4,
             'C1FA03',
             'C1FA05'),
            (0x00306511,
             'C1FA03',
             'C1FA05'),
            (0x00306540,
             'C1F803',
             'C1F805'),
            (0x00306565,
             '83E2E7',
             '83E29F'),
            (0x0030658F,
             'C1E103',
             'C1E105'),
            (0x001F9D1F,
             '0FBF05DCCBB50083F806740666B80100EB246A006A008B4D0C51681D0600006A608B550852E8E671000083C41866B80100EB03',
             '66833DDCCBB5000675206A038B4D0CE817C810006A006A00FF750C681D0600006A60FF7508E8E671000066B80100EB06909090'),
        ],
        'konditionsbonus': [
            # K35 (released 18.11.2026): texts 1358 / 1359 (private trainer, 'Konditionsbonus von 5%') only set / clear flag bit 13, which the
            # condition routine 0x00457E00 never read. New: plus 5 points for bit 13 (the mirror of the smoker's minus 5, text 1356
            # 'Konditionshandicap von 5%'), at most 100. The routine is rewritten in place; block from tools/asm_nacht.py.
            (0x00057E00,
             '558BEC83EC08894DF88B45F80FBF401699B964000000F7F9668945FE8B4DF8E8B5812A0085C074170FBF55FE83FA057D056633C0EB0D0FBF45FE83E805EB04668B45FE8BE55DC3CCCCCCCCCCCCCCCCCC',
             '510FBF411699B964000000F7F9508B4C2404E8C2812A0085C058740783E805790233C0508B4C2404E8B6822A0085C05859740D83C00583F8647E05B864000000C3909090909090909090909090909090'),
        ],
        'karriereende-1342': [
            # K36 (released 18.11.2026): text 1342 '... beschließt, seine Karriere als Fußballprofi zu beenden' only closed the firm state,
            # the player stayed. New: 0x0070E29E(player, club) after the message, as texts 338 and 716 do. Block from tools/asm_nacht.py.
            # Installer group: 'Spiellogik, größere oder nicht bekannte Auswirkung' (the first entry of that group).
            (0x001E26B9,
             '8B4D10E88E0B12000FBFD083FA0575256A068B4D10E8A30B12006A006A008B451050683E0500006A608B4D0C51E844E8010083C418',
             '8B4D10E88E0B12003C0575296A068B4D10E8A70B12006A006A00FF7510683E0500006A60FF750CE84AE80100FF7510E8B1BB120090'),
        ],
        'vorher-1309-1311': [
            # K43 (released 18.11.2026): messages 1309 / 1310 / 1311 showed 'before' with the per-flag allowances of the readers
            # (0x00700E3F, 0x007008B9, 0x00700C42) and 'after' without. New: 'before' is the stored value as well (writer with a
            # change of 0). Display only. Blocks from tools/asm_nacht.py.
            (0x001E184C,
             '8B4D10E8EBF51100668945FC8B4D10E859F01100668945F86A006A0A8B4D10E831EF110050668B4DF8516A006AF68B4D10E8A5F4110050668B55FC526A056A008B451050681D0500006A608B4D0C51E85EFD010083C430',
             '6A008B4D10E8D1F41100668945FC6A008B4D10E83DEF1100668945F86A006A0A8B4D10E82DEF110050FF75F86A006AF68B4D10E8A3F4110050FF75FC6A056A00FF7510681D0500006A60FF750CE860FD01009090909090'),
            (0x001E18D5,
             '8B4D10E865F31100668945FC6A006AFD8B4D10E880F1110050668B55FC526A016A008B451050681E0500006A608B4D0C51E838F7010083C424',
             '6A008B4D10E88EF11100668945FC6A006AFD8B4D10E87EF1110050FF75FC6A016A00FF7510681E0500006A60FF750CE83AF701009090909090'),
            (0x001E1940,
             '8B4D10E8FAF21100668945FC6A006AFB8B4D10E815F1110050668B55FC526A016A008B451050681F0500006A608B4D0C51E8CDF6010083C424',
             '6A008B4D10E823F11100668945FC6A006AFB8B4D10E813F1110050FF75FC6A016A00FF7510681F0500006A60FF750CE8CFF601009090909090'),
        ],
        'ehefrau-ereignisse': [
            # F06 (released 18.11.2026): the pre-routine 0x005FB634 of the wife events (0x005FB264: texts 1115, 1116, 1117, 1122, 1123,
            # 1124/1125, 1982) admitted only married players WITH a lover (0x006FFBE3 at 0x005FB6C5), so the events practically never
            # came. The only case that needs a lover (1123) tests her itself (0x005FB49A). New: married is enough - the 'je' after the
            # lover test is removed. Installer group: 'Spiellogik, größere oder nicht bekannte Auswirkung'.
            (0x001FB6C5,
             'E81945100085C07422',
             'E81945100085C09090'),
        ],
        'affaere-fliegt-auf': [
            # F01 (released 18.11.2026): 'the affair comes out' (0x005FB751: texts 1126, 1127, 1128, 1236) needs flag bit 2, which nothing
            # set. New: 0x007029A7 (new lover, texts 1251-1253) sets it; at 1126 the affair is ended after the message so that the
            # lover's name is still read. Blocks from tools/asm_nacht.py. Installer group: 'größere oder nicht bekannte Auswirkung'.
            (0x003029A7,
             '558BEC51894DFC6A32E85B7E080083C40425FF00000083C0328B4DFC0FBF1169D2540300008882D427C0008B45FC0FBF0869C95403000033D28A91D427C0008B45FC0FBF0869C95403000033C08A81D327C0003BD074B08BE55DC3',
             '516A32E8617E08005A04328B0C240FBF1169D2540300008882D427C0003A82D327C00074DC838A0427C0000459C3909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090'),
            (0x001FB7AB,
             '8B4D0CE85F74100025FF00000085C075538B4D0CE89E7110008B4D0CE8255A1000668945FC6A006AFB8B4D0CE8FD58100050668B55FC526A026A008B4D0CE8ED5F1000508B4D0CE8485F1000508B450C5068660400006A608B4D0851E8D35A000083C42C',
             '8B4D0CE85F74100084C075588B4D0CE8325A1000668945FC6A006AFB8B4D0CE80A59100050FF75FC6A026A008B4D0CE8FC5F1000508B4D0CE8575F100050FF750C68660400006A60FF7508E8E45A00008B4D0CE85F711000909090909090909090909090'),
        ],
        'hobby-1178-1179': [
            # F02 (released 18.11.2026): the dispatcher at 0x005FDBAE has four cases but drew random 0..1, so texts 1178 (wife moves to
            # her parents) and 1179 (broken arm, injury kind 46 for 21 days) never came. New: random 0..3 (push 2 -> push 4).
            (0x001FDBAE,
             '6A02',
             '6A04'),
        ],
        'bauverzoegerung-888-889': [
            # F03 (released 18.11.2026): the reasons for a building delay (table 0x0088EC8C, texts 878-889, 12 entries) were drawn with
            # random 0..9, so 888 and 889 never came. New: random 0..11 (push 0Ah -> push 0Ch). Texts 888 / 889 are corrected in the
            # text package.
            (0x00202373,
             '6A0A',
             '6A0C'),
        ],
        'handbuch-1173': [
            # F04 (released 18.11.2026): random 0..2 before four branches at 0x005FDA79; the fourth (text 1173, message only) never
            # came. New: random 0..3 (push 3 -> push 4).
            (0x001FDA79,
             '6A03',
             '6A04'),
        ],
        'vermittler-1481': [
            # F05 (released 18.11.2026): text 1481 (agent wants the young player to stay) tested 'age < 20' inside the branch
            # 'age >= 25'. New order: age < 20 (with the two unchanged conditions) -> 1481, else age < 25 -> 1480, else 1 in 100 ->
            # 1482. Block from tools/asm_nacht.py.
            (0x00368940,
             '8B4DE8E8D366F9FF0FBFD083FA197D120FBF45C40C04668945C466C745E6C805EB458B4DE8E8B166F9FF0FBFC883F9147D218B55E833C08A425483F80A7E148B4DE80FBE510883FA017D0866C745E6C905EB146A64E8761E020083C40485C0750666C745E6CA05',
             '8B4DE8E8D366F9FF6683F8147D178B55E8807A540A760E807A08017D0866C745E6C905EB426683F8197D0D66834DC40466C745E6C805EB2F6A64E8911E020083C40485C0752166C745E6CA05909090909090909090909090909090909090909090909090909090'),
        ],
        'trainer-eps': [
            # Historisches/Erfolgreichste Trainer, entry of a human manager (0x00725FBA): the column "EPs" only takes
            # counter 6 (Europapokale), "Sonstige" counters 3 + 10 + 13 + 15. Champions League wins (counter 4) and
            # European Supercups (counter 9) are dropped, while computer coaches get both (0x006B53D4).
            # See docs/befund-trainer-eps.md. The 81 bytes at VA 0x00725FF0 are rewritten without the repeated
            # pointer reloads; eax, ecx and edx are reloaded right after the block (0x00726041..).
            (0x00325FF0,
             '8B450C668B0866894DF48B550C668B4202668945F68B4D0C668B510C668955F8'
             '8B450C0FBF48148B550C0FBF420603C88B550C0FBF421E03C88B550C0FBF421A'
             '03C866894DFC8B4D0C668B5116668955FA',
             '8B450C'            # mov eax,[ebp+0Ch]   pointer to the counters
             '668B08'            # mov cx,[eax]        championships
             '66894DF4'          # mov [ebp-0Ch],cx
             '668B4802'          # mov cx,[eax+2]      cups
             '66894DF6'          # mov [ebp-0Ah],cx
             '668B480C'          # mov cx,[eax+0Ch]    Europapokale
             '66034808'          # add cx,[eax+8]      + Champions League wins (new)
             '66894DF8'          # mov [ebp-8],cx
             '668B4814'          # mov cx,[eax+14h]    Weltpokale
             '66034806'          # add cx,[eax+6]      + Liga-/Supercup
             '6603481E'          # add cx,[eax+1Eh]    + world championships
             '6603481A'          # add cx,[eax+1Ah]    + European championships
             '66034812'          # add cx,[eax+12h]    + European Supercups (new)
             '66894DFC'          # mov [ebp-4],cx
             '668B4816'          # mov cx,[eax+16h]    promotions
             '66894DFA'          # mov [ebp-6],cx
             + '90' * 19),
        ],
    },
    # D3D_Dll.dll (SGL engine) shipped with 1.40 (GOG)
    '16830FBB5CE0B43E514791BD81BCB1B99B3E9D7D2294E9A4FE25098A57377032': {
        'text-groesse': [
            # .text VirtualSize 0x5422E -> 0x54300 so the code caves at 0x59240.. lie inside the section
            # (next section starts at 0x5A000). Needed by every cave patch below.
            (0x00000210, '2E420500', '00430500'),
        ],
        'clipping-aus': [
            # End of the "apply all render states" routine 0x0502D8F0: additionally call
            # IDirect3DDevice3::SetRenderState(D3DRENDERSTATE_CLIPPING = 136, FALSE). SGL clips its 2D polygons
            # itself; with clipping on, d3d9 clips every vertex on the CPU (hot loop on the RX 6800 XT).
            # The device pointer address is read from the relocated instruction at 0x0502D8F8 (position independent).
            (0x0002DD29, '5B5E8BE55DC3', 'E942B5020090'),   # jmp 0x05059270, nop
            (0x00059270, '00' * 37,
             'E800000000'        # call next
             '59'                # pop ecx
             '8B898446FDFF'      # mov ecx,[ecx-0x2B97C]  (= relocated &g_device from 0x0502D8F9)
             '8B01'              # mov eax,[ecx]
             '85C0'              # test eax,eax
             '740D'              # je epilogue
             '6A00'              # push FALSE
             '6888000000'        # push 136 (D3DRENDERSTATE_CLIPPING)
             '50'                # push device
             '8B10'              # mov edx,[eax]
             'FF5258'            # call [edx+58h]  SetRenderState
             '5B5E8BE55DC3'),    # original epilogue: pop ebx, pop esi, mov esp,ebp, pop ebp, ret
        ],
        'settexture-cache': [
            # SetTexture wrapper 0x0502D290: skip IDirect3DDevice3::SetTexture(0, tex) when tex equals the
            # cached current texture [0x0508A7A0]. Jump at 0x0502D29B into a code cave at 0x05059240
            # (end of .text, mapped, unused). The cave reads the relocated address of the cache variable
            # from the existing store instruction at 0x0502D2C1, so it works at any load address.
            (0x0002D29B, '8B550885C0741D', 'E9A0BF02009090'),
            (0x00059240, '00' * 36,
             '8B5508'            # mov edx,[ebp+8]
             '85C0'              # test eax,eax
             '0F847440FDFF'      # je 0x0502D2BF        (no device: store and return)
             'E800000000'        # call next
             '59'                # pop ecx              (ecx = address of next)
             '8B897140FDFF'      # mov ecx,[ecx-0x2BF8F] (= relocated &cache from 0x0502D2C1)
             '3B11'              # cmp edx,[ecx]
             '0F846640FDFF'      # je 0x0502D2C5        (same texture: return)
             'E93E40FDFF'),      # jmp 0x0502D2A2       (original call path)
        ],
    },
    # ddraw.dll = "GOG.com DirectX 1-7 wrapper" shipped with the GOG release (image base 0x18000000)
    # deb/MeineDialoge.rch (GOG): dialogs and interface texts, loaded by 0x004318FA. String table entries are
    # [id word][text, zero-terminated]; "\t" is written out as backslash + t.
    'AA68E14E697CE944CBF3AF4F8AE1769965597B3BB6087A9BE01B32006E927536': {
        'tagesform-ueberschrift': [
            # Text 4746 "Pl.\tVerein\tForm" (header of the league statistic "Tagesform"): the column holds the team's
            # average grade (see 'tagesform' above), not the players' form. "Form" -> "Note", same length.
            # The site covers the whole entry (id 0x128A, text, terminating zero; "Form" starts at 0x2FC33), so that
            # the installer recognises any other edition of the text file as unknown instead of matching four bytes.
            (0x0002FC24, '8A12' '506C2E5C7456657265696E5C74' '466F726D' '00',
                         '8A12' '506C2E5C7456657265696E5C74' '4E6F7465' '00'),
        ],
    },
    'B2CB0FD03C1D1A0401E0468DAADE7B6D2A33D3EA75897F3E836D68E1E85C3440': {
        'hw-vertexverarbeitung': [
            # The wrapper stores bit 9 of D3DCAPS9.PrimitiveMiscCaps (D3DPMISCCAPS_CLIPTLVERTS) in [0x1845911C].
            # If it is 0 (RX 6800 XT driver 32.0.21045.16010), it calls SetSoftwareVertexProcessing(TRUE) after
            # CreateDevice/Reset (0x1801D031, 0x1801E6AD, 0x18020197). d3d9 then computes clip codes for every vertex
            # by reading them back from a write-combined buffer (measured ~600x slower, analyse/profil_reg.txt).
            # Patch: store 1 instead of the caps bit, so the device stays in hardware vertex processing.
            (0x0001CC47, 'C1E80923C5', 'B801000000'),   # shr eax,9 / and eax,ebp -> mov eax,1  (VA 0x1801CC47)
            (0x0001E2BE, 'C1E80923C5', 'B801000000'),   # same in the second init path          (VA 0x1801E2BE)
        ],
    },
}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    data = bytearray(open(src, 'rb').read())
    sha = hashlib.sha256(data).hexdigest().upper()
    if sha not in TARGETS:
        sys.exit(f'unknown input file (SHA-256 {sha})')
    patches = TARGETS[sha]
    for pid in sys.argv[3:] or list(patches):
        for off, old, new in patches[pid]:
            old, new = bytes.fromhex(old), bytes.fromhex(new)
            if data[off:off + len(old)] != old:
                sys.exit(f'{pid}: unexpected bytes at 0x{off:X}: {data[off:off + len(old)].hex()}')
            data[off:off + len(new)] = new
        print(f'applied {pid}')
    open(dst, 'wb').write(data)
    print(f'written {dst}, SHA-256 {hashlib.sha256(data).hexdigest().upper()}')


if __name__ == '__main__':
    main()
