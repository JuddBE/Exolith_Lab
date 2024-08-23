
Exolith Regolith Sintering Stand
===================
This repository contains the code responsible for controlling an automated regolith sintering stand. The stand is used to sinter regolith, which is a mixture of solid particles that form the surface of a planet or a moon, into solid structures.

***Requirements***

Python 3.6 or higher

***Getting Started***

Clone this repository to your local machine using 

***_git clone_ https://github.com/JuddBE/Exolith_Lab***

Install the required packages using _pip install -r requirements.txt_.

Interface with the regolith sintering stand to your computer over wifi/ethernet using ssh.

**How to run**
Run _python3 solarAlignment.py_ to start the automated tracking process to align the lens with the sun.

Run _python3 runGcode.py [name of gcode file]_ to start printing a specific GCODE file.

Use the app for ease of use, which is pinned on the Exolith sintering slack channel and does not require interfacing with a terminal.

(The code provides a command-line interface that allows you to control the regolith sintering stand.) The following commands are available:

python3 xMoveCoord.py [coord] [optional: speed 0-1]
python3 yMoveCoord.py [coord] [optional: speed 0-1]
python3 zMoveCoord.py [coord] [optional: speed 0-1]
python3 runGcode.py [name of gcode file]
python3 shapes.py ["box3d", "box2d", "circle", "cylinder"]

***Contributions***

Contributions are welcome. If you find a bug or have an idea for a new feature, please open an issue or a pull request.

***License***

This project is licensed under Exolith Lab License.

Semantic Versioning
===================
_Applies to Releases Only_

Semantic Versioning (SemVer) is a widely used standard for software versioning. It provides a simple and consistent method for versioning software projects and helps communicate version changes to stakeholders.

SemVer consists of three parts:

**Major version number:** This number changes when there are breaking changes to the software. Breaking changes are any changes that would require existing software to be modified or upgraded to work with the new version.

**Minor version number:** This number changes when new features are added to the software. The features are non-breaking and should not impact existing functionality.

**Patch version number:** This number changes when bug fixes are made to the software. These changes should not affect the functionality of the software.

SemVer uses the format of **Major.Minor. Patch.** For example, **2.0.0 or 1.1.3.**
