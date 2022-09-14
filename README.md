## Kitchen
This repository, _Kitchen_, represents a part of a bigger project of a restaurant simulation,
performed as laboratory work during the _Network Programming_ course. The another component of
this project, _Dinning Hall_, can be found following this 
[link](https://github.com/MrCrowley21/Dinning_Hall.git). \
!**Note** the fact that this version of README file is not final and will be modified  further.\
First, to run the project into a docker container, perform the following commands:
````
$ docker network create restaurant_network  
$ docker build -t kitchen_image .  
$ docker run --net restaurant_network -p 8080:8080 --name kitchen_container kitchen_image
````
The first line will create an image of our project, while the next one - run project inside 
the created container. \
**NOTE** that this container should be run first and then, the _Dinning Hall_ container 
could be run.
The _Kitchen_ project consists of:
* a _README_ file with explanations;
* a _Dockerfile_ to assemble the image;
* a _requirements.txt_ file that contains all necessary libraries the program to run properly;
* a _server.py_ file that starts the server and program execution;
* a _config.py_ file that contains defined constants and global variables;
* a _kitchen_data_ map that contains json files with cooks and food items from menu;
* a _Components_logic_ map that contains classes that defines each project entity behaviour.

For this moment, for more explanation regarding the code itself, please take a look at the comments 
that appears there.