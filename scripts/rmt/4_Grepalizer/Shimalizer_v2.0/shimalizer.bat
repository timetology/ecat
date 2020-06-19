@echo off
echo.
echo.Script:	Shimalizer v2.6
echo.Author: The Goat Factory
echo.Date:	2020-06-18
echo.Legal1: Got Milk?
echo.Legal2:	Milk it!

mkdir \tmp
echo.
echo Processing SHIM file: %1
echo.
mkdir %1-Results
echo Saving results to: %1-Results
echo.

echo Processing web directories....
REM Reserved names frequency analysis
grep -i -E "(tomcat|inetpub|wwwroot|webapps|clientaccess)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\webFolders.txt
echo "================================================================================================================" >> %1-Results\webFolders.txt
grep -i -E "(tomcat|inetpub|wwwroot|webapps|clientaccess)" %1 >> %1-Results\webFolders.txt

echo Processing reserved names....
REM Reserved names frequency analysis
grep -i -E "(explorer.exe|iexplore.exe|svchost.exe|ctfmon.exe|dllhost.exe)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\reservedNames.txt
echo "================================================================================================================" >> %1-Results\reservedNames.txt
grep -i -E "(explorer.exe|iexplore.exe|svchost.exe|ctfmon.exe|dllhost.exe)" %1 >> %1-Results\reservedNames.txt

echo Processing Windows folder..
REM Frequency Analysis Windows folder
grep -i -E "(:\\windows\\.{1,15},)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\Windowsfolder.txt
echo "================================================================================================================" >> %1-Results\Windowsfolder.txt
grep -i -E "(:\\windows\\.{1,15},)" %1 >> %1-Results\Windowsfolder.txt

echo Processing system32 folder...
REM Frequency analysis system32 folder
grep -i -E "(\\system32\\)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\sys32folder.txt
echo "================================================================================================================" >> %1-Results\sys32folder.txt
grep -i -E "(\\system32\\)" %1 >> %1-Results\sys32folder.txt

echo Processing Any TEMP folder...
REM Frequency analysis TEMP folder
grep -i -E "(\\temp\\)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\anytempfolder.txt
echo "================================================================================================================" >> %1-Results\anytempfolder.txt
grep -i -E "(\\temp\\)" %1 >> %1-Results\anytempfolder.txt

echo Processing first level TEMP folder...
REM Frequency analysis TEMP folder
grep -i -E "(:\\temp\\)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\tempfolder.txt
echo "================================================================================================================" >> %1-Results\tempfolder.txt
grep -i -E "(:\\temp\\)" %1 >> %1-Results\tempfolder.txt

echo Processing AppData folder...
REM Frequency analysis TEMP folder
grep -i -E "(\\appdata\\)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\appdatafolder.txt
echo "================================================================================================================" >> %1-Results\appdatafolder.txt
grep -i -E "(\\appdata\\)" %1 >> %1-Results\appdatafolder.txt

echo Processing Downloads folder...
REM Frequency analysis TEMP folder
grep -i -E "(\\downloads\\)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\downloadsfolder.txt
echo "================================================================================================================" >> %1-Results\downloadsfolder.txt
grep -i -E "(\\downloads\\)" %1  >> %1-Results\downloadsfolder.txt

echo Processing 0-99 byte size files...
REM Frequency analysis files with >100 byte size
grep -E "\,([0-9]{2})\,N\/A" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\LessThan100bytes.txt
echo "================================================================================================================" >> %1-Results\LessThan100bytes.txt
grep -E "\,([0-9]{2})\,N\/A" %1 >> %1-Results\LessThan100bytes.txt

echo Processing 100-999 byte size files...
REM Frequency analysis files with >100 byte size
grep -E "\,([0-9]{3})\,N\/A" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\Files100-999bytes.txt
echo "================================================================================================================" >> %1-Results\Files100-999bytes.txt
grep -E "\,([0-9]{3})\,N\/A" %1  >> %1-Results\Files100-999bytes.txt

echo Processing TMP folder...
REM Frequency analysis TMP folder
grep -i -E "(\\tmp\\)" %1 | grep -E -v "(\{|\_|\-|\~|\()" | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\tmpfolder.txt
echo "================================================================================================================" >> %1-Results\tmpfolder.txt
grep -i -E "(\\tmp\\)" %1 | grep -E -v "(\{|\_|\-|\~|\()" >> %1-Results\tmpfolder.txt

echo Processing 2 char filenames...
REM Two char filenames.
grep "\\..\....," %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\2char.txt
echo "================================================================================================================" >> %1-Results\2char.txt
grep "\\..\....," %1  >> %1-Results\2char.txt

echo Processing files with suspicious extensions...
REM Files with Suspicious extensions
echo "================================================================================================================" > %1-Results\suspectExtension.txt
grep -E -v -i "(\.exe,|\.dll,|\.tmp,)" %1 | grep -v -i "Recycle\.Bin" | cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\suspectExtension.txt
echo "================================================================================================================" >> %1-Results\suspectExtension.txt
grep -E -v -i "(\.exe,|\.dll,|\.tmp,)" %1 >> %1-Results\suspectExtension.txt

echo Processing files with interesting extensions...
REM Files with interesting extensions
echo "================================================================================================================" > %1-Results\interestingExtensions.txt
grep -E -i "(\.bin,|\.dat,|\.log,|\.gif,|\.txt,|\.jpg,|\.rar,|\.tar,|\.sql,|\.zip,)" %1  | cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\interestingExtensions.txt
echo "================================================================================================================" >> %1-Results\interestingExtensions.txt
grep -E -i "(\.bin,|\.dat,|\.log,|\.gif,|\.txt,|\.jpg,|\.rar,|\.tar,|\.sql,|\.zip,)" %1 >> %1-Results\interestingExtensions.txt

echo Processing filenames with .tmp extension...
REM Files with TMP extensions
grep -E -i "(\.tmp,)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\tmpExtension.txt
echo "================================================================================================================" >> %1-Results\tmpExtension.txt
grep -E -i "(\.tmp,)" %1 >> %1-Results\tmpExtension.txt

echo Processing 1 char filenames...
REM One char filename with any extension.
grep "\\.\....," %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\1char.txt
echo "================================================================================================================" >> %1-Results\1char.txt
grep "\\.\....," %1 >> %1-Results\1char.txt


echo Processing files one directory deep...
REM One level deep files:
grep -E "(:\\[a-zA-Z0-9]{1,12}\\[a-zA-Z0-9]*\....,)" %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\1deep.txt
echo "================================================================================================================" >> %1-Results\1deep.txt
grep -E "(:\\[a-zA-Z0-9]{1,12}\\[a-zA-Z0-9]*\....,)" %1  >> %1-Results\1deep.txt


echo Processing self-extracting folders...
REM Self-extracting exes
grep -i "\\Rar\$" %1  > %1-Results\selfExtracting.txt


echo Processing batch filenames...
REM Frequency analysis of batch files with 1 - 10 character long filenames
grep -i -E "(\\.{1}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr  > %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{2}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{3}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{4}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{5}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{6}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{7}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{8}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{9}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{10}\.bat,)" %1 |  cut -d, -f4 | sort | uniq -c -i | sort -nr >> %1-Results\BATextension.txt
echo "================================================================================================================" >> %1-Results\BATextension.txt
grep -i -E "(\\.{1,10}\.bat,)" %1 >> %1-Results\BATextension.txt


echo Processing keywords in ioc-terms.txt file...
REM HITS from specified IOCs.
echo.>%1-Results\IOC-Results.txt
for /F "tokens=*" %%i in (./ioc-terms.txt) do (
	echo "===================================================">>%1-Results\IOC-Results.txt
	echo %%i HITS>>%1-Results\IOC-Results.txt
	echo "===================================================">>%1-Results\IOC-Results.txt
	grep -E -i %%i %1>>%1-Results\IOC-Results.txt
)
echo.
echo.


echo Processing keywords in ioc-dates-terms.txt file...
REM HITS from specified IOCs.
echo.>%1-Results\IOC-Dates-Results.txt
for /F "tokens=*" %%i in (./ioc-dates.txt) do (
	echo "===================================================">>%1-Results\IOC-dates-Results.txt
	echo %%i HITS>>%1-Results\IOC-dates-Results.txt
	echo "===================================================">>%1-Results\IOC-dates-Results.txt
	grep -i %%i %1>>%1-Results\IOC-dates-Results.txt
)
echo.



