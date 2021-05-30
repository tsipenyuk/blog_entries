# blog_entries

Code that accompanies some of my [blog entries](tsipenyuk.wordpress.com).

@ECHO OFF

REM This batch file allows you to rip all tracks from an audio CD to MP3 or WAV.
REM However, it must be adapted to the individual circumstances.
REM Typically this batch file is called from a batch file that sets the artist, album, number of tracks, and track song titles.

REM Acquired from Dec 2016 post by kodela at:
REM https://forum.videolan.org/viewtopic.php?t=136816#p451471

REM Changes made Jun 2019 by NOYB:
REM Added vlc --noloop command line option to keep from ending up with zero length files.
REM Parameterized most of the vlc command line options to increase flexibility.
REM Added quotes around the dst value on vlc command line to support folder and file names containing spaces.
REM Added renaming the generic Track_nn file to Artist, Album, Track #, Track Title.
REM Re-factored to eliminate the with_zero and without_zero sub routines.

REM Changes made May 2020 by BobR2
REM Introduced a Num_of_Tracks variable and re-factored to manage track titles as an array.
REM Modified the FOR loop so as to not depend on having the CD be represented as containing a set of "*.cda" files (not all Compact Disk Digital Audio (CD-DA) CDs do)

REM Ampersand (&) in variables must be escaped (^&).
REM Dynamic variables and those that may contain escaped ampersand (^&) need delayed expansion (!var!).
SETLOCAL ENABLEDELAYEDEXPANSION

REM *****
REM *** Begin user defined parameters
REM *****

REM *****     enter after "SET p=" the destination directory for ribbed tracks    *****
SET p=C:\Users\%USERNAME%\Desktop\VLC CD RIP\!Artist!\!Album!\

REM *****     enter after "SET m=" for conversion to MP3 > "MP3", to WAV > "WAV"  *****
SET m=wav

REM *****     enter after "SET s=" the source directory for the optical drive     *****
SET s=D:\

SET samplerate=44100
SET channels=2

REM *****     enter after "CD " the installation directory of vlc.exe             *****
SET vlc_cmd=C:\Program Files\VideoLAN\VLC\vlc

REM *****     enter after "SET dry_run=" anything other than "false" (case insensitive) to make a test run without transcoding.     *****
SET dry_run=false

REM *****
REM *** End user defined parameters
REM *****


REM *****
REM *** Everything below here is expected to be directed by the above parameters.
REM *****

REM Set the transcoder parameters.
if /i %m%==MP3 (
	SET acodec=mp3
	SET ab=128
	SET mux=raw
) ELSE if /i %m%==WAV (
	SET acodec=s16l
	SET ab=224
	SET mux=wav
) ELSE (
	ECHO The specified output type %m% is not valid.
	ECHO The output type must be either "MP3" or "WAV".
	EXIT
)

IF NOT EXIST "!s!" (
	ECHO The source location does not exist.
	ECHO !s!
	ECHO Press any key to abort.
	PAUSE >nul
	EXIT
)

IF NOT EXIST "!p!" (
	MKDIR "!p!"
) ELSE (
	ECHO The destination folder already exists.
	ECHO Continuing may delete existing content from this folder:
	ECHO !p!
	CHOICE /C "YN" /M "Do you want to continue anyway?"
	IF ERRORLEVEL 2 EXIT
)
CD "!p!"
ECHO Target folder:
ECHO !p!

REM Loop through the source tracks to transcode them.
FOR /L %%I In (1,1,%Num_of_Tracks%) DO (CALL :transcode %%I)

ECHO Finished - Press any key to close.
PAUSE >nul

GOTO :eof

:transcode
	REM Set the two-digit track number with leading zero as needed
	IF %1 LEQ 9 (CALL SET ii=0%1) ELSE (CALL SET ii=%1)
	
	ECHO Transcoding Track %1 (!ii!) - !Track_Title[%1]!

	IF /i %dry_run%==false (
		CALL "!vlc_cmd!" -I http cdda:///%s% --cdda-track=%1 :sout=#transcode{vcodec=none,acodec=%acodec%,ab=%ab%,channels=%channels%,samplerate=%samplerate%}:std{access="file",mux=%mux%,dst="!p!Track_!ii!.%m%"} --noloop vlc://quit
		REN "!p!Track_!ii!.%m%" "!Artist!%d%!Album!%d%!ii!%d%!Track_Title[%1]!.%m%"
	)
:eof
