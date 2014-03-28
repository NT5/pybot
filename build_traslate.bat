@echo off
set output_dir=locale
set input_file=res/commands.py
set domain=commands
set output_lang=es_ES
set PATH=C:\Program Files (x86)\GnuWin32\bin;%path%

goto mo

:mk
mkdir %output_dir%\%output_lang%\LC_MESSAGES
:pot
xgettext --language=Python -o %output_dir%/%domain%_%output_lang%.pot %input_file%
echo Plantillas creadas
echo.
echo Esperando edicion
start notepad.exe "%output_dir%/%domain%_%output_lang%.pot"
pause
:po
msginit -i %output_dir%/%domain%_%output_lang%.pot -o %output_dir%/%output_lang%.po
echo Fichero de traduccion creado!
echo.
pause&exit
:mo
msgfmt %output_dir%/%output_lang%.po -o %output_dir%/%output_lang%/LC_MESSAGES/%domain%.mo
echo Binario creado!
echo.
pause&exit