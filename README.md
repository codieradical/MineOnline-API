# MineOnline API
This API acts as a companion to the live Minecraft APIs to re-enable old, deprecated web services.

## Restored and Recreated Features
These are features which are no longer available through official servers.

- Server Authentication

- Skins and Cloaks

- Server List

- Online World Saves

## Serving Assets
The API is written to serve files that used to be (and sometimes still are) hosted on AWS.
The recommended file tree is as follows:

public/
```
│
├───MinecraftResources                    from http://s3.amazonaws.com/MinecraftResources/
│   │   download.xml                      This is the index document tree from that url ^
├───resources                             Sound files for older minecraft versions.
│   │   index.txt                         A list of each sound file. Has extra data.
|
```

## The Database

The Mongo Database contains two Collections.

- Serverjoins

These are created for server authentication when a logged in player attempts to join a server.
If the server is in online-mode, it will only allow joins if a serverjoin exists, then the serverjoin is deleted.

- Classicservers

These are classic servers displayed on the server list.
Documents are created on server heartbeat, and expire after about a minute and a half unless another heartbeat request is received.
These are used to get server information such as salt, ip and port from the server ID, which makes it necessary for classic server authentication.
