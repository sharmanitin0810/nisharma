@echo off
echo Merging QXDM Log files 
cd input-log
perl "C:\Users\Field QXDM-PC\Desktop\test\input-log\MergeFiles.pl"
echo Press enter to generate Analyzers from Mergedfile
pause
perl "C:\Users\Field QXDM-PC\Desktop\test\ExportTextAndExcel.pl"
echo All Analyzers are Exported Successfully
pause