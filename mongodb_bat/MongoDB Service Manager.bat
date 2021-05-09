@echo off
rem mongoDB 服务
echo.
echo.
echo.
echo.
echo.		+*****************  MongoDB Service Manager ************+
echo. 		*		      1.start   MongoDB 		*
echo. 		*		      2.stop   MongoDB 			*
echo. 		*		      3.status MongoDB			*
echo. 		+*******************************************************+
echo. [3hex]
color F0
echo. Tip:Use administrator privilege to run!!!
echo. http://localhost:27017/

:loop

echo.
set/p a=Choose:

if %a%==1 start  cmd /k net start MongoDB 
if %a%==2 start  cmd /k net stop MongoDB 
if %a%==3 start  cmd /k "net start | find /i "MongoDB""

goto loop