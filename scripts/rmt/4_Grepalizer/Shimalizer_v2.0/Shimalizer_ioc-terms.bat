@echo off
echo.
echo.Script:	Shimalizer v2.0 IOC-Terms.txt only
mkdir %1-Results
echo Saving results to: %1-Results
echo.

echo Processing keywords in ioc-dates-terms.txt file...
REM HITS from specified IOCs.
echo.>%1-Results\IOC-terms-Results.txt
for /F "tokens=*" %%i in (./ioc-terms.txt) do (
	echo "===================================================">>%1-Results\IOC-terms-Results.txt
	echo %%i HITS>>%1-Results\IOC-terms-Results.txt
	echo "===================================================">>%1-Results\IOC-terms-Results.txt
	grep -i %%i %1 | cut -d, -f4 | sort | uniq -c -i | sort -nr > %1-Results\IOC-terms-Results.txt
	echo "================================================================================================================" >> IOC-terms-Results.txt
	grep -i %%i %1>>%1-Results\IOC-terms-Results.txt
)
echo.