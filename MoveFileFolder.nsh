;%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
; MoveFile and MoveFolder macros
;
; Author:  theblazingangel@aol.com (for the AutoPatcher project - www.autopatcher.com)
; Created: June 2007
;%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

;==================
; MoveFile macro
;==================

    !macro MoveFile sourceFile destinationFile

	!define MOVEFILE_JUMP ${__LINE__}

	; Check source actually exists

	    IfFileExists "${sourceFile}" +3 0
	    SetErrors
	    Goto done_${MOVEFILE_JUMP}

	; Add message to details-view/install-log

	    DetailPrint "Moving/renaming file: ${sourceFile} to ${destinationFile}"

	; If destination does not already exists simply move file

	    IfFileExists "${destinationFile}" +3 0
	    Rename "${sourceFile}" "${destinationFile}"
	    Goto done_${MOVEFILE_JUMP}

	; If overwriting without 'ifnewer' check

	    ${If} $switch_overwrite == 1
		Delete "${destinationFile}"
		Rename "${sourceFile}" "${destinationFile}"
		Delete "${sourceFile}"
		Goto done_${MOVEFILE_JUMP}
	    ${EndIf}

	; If destination already exists

	    Push $R0
	    Push $R1
	    Push $R2
	    Push $R3

	    GetFileTime "${sourceFile}" $R0 $R1
	    GetFileTime "${destinationFile}" $R2 $R3

	    IntCmp $R0 $R2 0 older_${MOVEFILE_JUMP} newer_${MOVEFILE_JUMP}
	    IntCmp $R1 $R3 older_${MOVEFILE_JUMP} older_${MOVEFILE_JUMP} newer_${MOVEFILE_JUMP}

	    older_${MOVEFILE_JUMP}:
	    delete "${sourceFile}"
	    goto time_check_done_${MOVEFILE_JUMP}

	    newer_${MOVEFILE_JUMP}:
	    Delete "${destinationFile}"
	    Rename "${sourceFile}" "${destinationFile}"
	    Delete "${sourceFile}" ;incase above failed!

	    time_check_done_${MOVEFILE_JUMP}:

	    Pop $R3
	    Pop $R2
	    Pop $R1
	    Pop $R0

	done_${MOVEFILE_JUMP}:

	!undef MOVEFILE_JUMP

    !macroend

;==================
; MoveFolder macro
;==================

    !macro MoveFolder source destination mask

	!define MOVEFOLDER_JUMP ${__LINE__}

	Push $R0
	Push $R1

	; Move path parameters into registers so they can be altered if necessary

	    StrCpy $R0 "${source}"
	    StrCpy $R1 "${destination}"

	; Sort out paths - remove final backslash if supplied

	    Push $0

	    ; Source
	    StrCpy $0 "$R0" 1 -1
	    StrCmp $0 '\' 0 +2
	    StrCpy $R0 "$R0" -1

	    ; Destination
	    StrCpy $0 "$R1" 1 -1
	    StrCmp $0 '\' 0 +2
	    StrCpy $R1 "$R1" -1

	    Pop $0

	; Create destination dir

	    CreateDirectory "$R1\"

	; Add message to details-view/install-log

	    DetailPrint "Moving files: $R0\${mask} to $R1\"

	; Push registers used by ${Locate} onto stack

	    Push $R6
	    Push $R7
	    Push $R8
	    Push $R9

	; Duplicate dir structure (to preserve empty folders and such)

	    ${Locate} "$R0" "/L=D" ".MoveFolder_Locate_createDir"

	; Locate files and move (via callback function)

	    ${Locate} "$R0" "/L=F /M=${mask} /S= /G=1" ".MoveFolder_Locate_moveFile"

	; Delete subfolders left over after move

	    Push $R2
	    deldir_loop_${MOVEFOLDER_JUMP}:
	    StrCpy $R2 0
	    ${Locate} "$R0" "/L=DE" ".MoveFolder_Locate_deleteDir"
	    StrCmp $R2 0 0 deldir_loop_${MOVEFOLDER_JUMP}
	    Pop $R2


	; Pop registers used by ${Locate} off the stack again

	    Pop $R9
	    Pop $R8
	    Pop $R7
	    Pop $R6

	; Delete source folder if empty

	    RMDir "$R0"

	Pop $R1
	Pop $R0

	!undef MOVEFOLDER_JUMP

    !macroend

;==================
; MoveFolder macro's ${Locate} callback functions
;==================

	Function .MoveFolder_Locate_createDir

	    ${If} $R6 == ""
		Push $R2
		StrLen $R2 "$R0"
		StrCpy $R2 $R9 '' $R2
		CreateDirectory "$R1$R2"
		Pop $R2
	    ${EndIf}

	    Push $R1

	FunctionEnd

	Function .MoveFolder_Locate_moveFile

	    Push $R2

	    ; Get path to file

		StrLen $R2 "$R0"
		StrCpy $R2 $R9 '' $R2
		StrCpy $R2 "$R1$R2"

	    ; If destination does not already exists simply move file

		IfFileExists "$R2" +3 0
		Rename "$R9" "$R2"
		Goto done

	    ; If overwriting without 'ifnewer' check

		${If} $switch_overwrite == 1
		    Delete "$R2"
		    Rename "$R9" "$R2"
		    Delete "$R9"
		    Goto done
		${EndIf}

          ; If never overwriting

            ${If} $switch_overwrite == 2
                Goto done
            ${EndIf}

	    ; If destination already exists

		Push $0
		Push $1
		Push $2
		Push $3

		GetFileTime "$R9" $0 $1
		GetFileTime "$R2" $2 $3

		IntCmp $0 $2 0 older newer
		IntCmp $1 $3 older older newer

		older:
		Delete "$R9"
		Goto time_check_done

		newer:
		Delete "$R2"
		Rename "$R9" "$R2"
		Delete "$R9" ;incase above failed!

		time_check_done:

		Pop $3
		Pop $2
		Pop $1
		Pop $0

	    done:

	    Pop $R2

	    Push $R1

	FunctionEnd

	Function .MoveFolder_Locate_deleteDir

	    ${If} $R6 == ""
		RMDir $R9
		IntOp $R2 $R2 + 1
	    ${EndIf}

	    Push $R1

	FunctionEnd