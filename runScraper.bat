: # this should work in both linux or windows cmd using the GOTO technique

:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL

echo "this part should only run in linux"
echo "if ur using fish this aint gonna work bud, but you can run this using bass"
python --version # Fix if its broken later
if [$? -eq 0 ]; then
    echo "python installed"
else
    echo "python not detected. Please go to the python website and install it."
    exit $?
fi

pip --version 
if [$? -eq 0 ]; then
    echo "pip installed"
else
    echo "pip not detected. "
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
fi

cd env
if [$? -eq 0 ]; then
    echo "env file found. Running virtual environment..."
else
    echo "env file not found. Checking if env is installed..."
    virtualenv --version
    if [$? -eq 0 ]; then
        echo "env installed. Creating env file..."
    else
        echo "env not detected. Installing env..."
        python 3 -m pip install --user virtualenv
    fi
    python 3 -m venv env
fi

sh Scripts/activate
cd ..

echo "virtual environment activated, checking requirements"

pip install -r requirements.txt
if [$? -eq 0 ]; then
    echo "requirements updated. Running python script..."
else
    echo "requirements file not found. Please install it to this directory"
    exit $?
fi

python getData.py 
if [$? -eq 0 ]; then
    echo "success"
else
    echo "python script not found. Please install the python script to the directory"
fi

exit $?

:CMDSCRIPT
ECHO this should only run in windows
:: checking python installation
python --version 2>NUL
if ERRORLEVEL 1 GOTO errNoPy

GOTO :pyIn

:errNoPy
ECHO python is not installed on your machine. Attempting to install now...
:: download installer
curl "https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe" -o python-installer.exe
:: run installer
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
:: refresh env variables - will leave out for now because am lazy xd
:: call RefreshEnv.cmd
:: start "" "https://www.python.org/downloads/windows/"
GOTO :EOF

:pyIn
ECHO python detected. Checking pip...
:: check if pip is installed, and if not install it
pip --version 2>NUL
if ERRORLEVEL 1 GOTO errNoPip

GOTO :goodPip

:errNoPip
ECHO pip is not installed on your machine. Attempting to install now...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
ECHO Succeessfully installed pip

:goodPip
ECHO pip detected. Starting virtual environment...
:: check if env file is in the right spot
if exist env (
    ECHO env file detected. Starting virtual environment...
) else (
    ECHO env file not detected. Checking if env is installed...
    virtualenv --version 2>NUL
    if ERRORLEVEL 1 GOTO instEnv

    GOTO :instEnvFile

    :instEnv
    ECHO env not installed. Installing now...
    py -m pip install --user virtualenv

    :instEnvFile
    ECHO Installing file for virtual environment...
    py -m venv env
)

:: activate virtual environment
call env\Scripts\activate.bat
ECHO virtual environment activated. Checking requirements file...

:: check if the requirements file is here
if exist requirements.txt (
    ECHO requirements file found. Checking if dependencies need updating...
    pip install -r requirements.txt
) else (
    ECHO requirements file not found. Please put requirements.txt in the correct folder.
    GOTO :EOF
)

:: check if python script exists
if exist getData.py (
    ECHO python script found. Running script...
    python getData.py
) else (
    ECHO python script not found. Please install it in the correct directory
    GOTO :EOF
)