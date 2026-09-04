@echo off
setlocal enabledelayedexpansion
set "JAVA=C:\Users\Aaryan Rawat\AppData\Local\Coursier\cache\arc\https\github.com\adoptium\temurin17-binaries\releases\download\jdk-17.0.20.1%%2B1\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1.zip\jdk-17.0.20.1+1\bin\java.exe"
set "CP=out"
for /f "delims=" %%i in ('"C:\Users\Aaryan Rawat\AppData\Local\Coursier\data\bin\cs.bat" fetch org.scala-lang:scala3-library_3:3.9.0') do (
    set "CP=!CP!;%%i"
)
"%JAVA%" -cp "!CP!" kuwala.Main
