datavisualization

run the container with: 

docker run --name graphviz -p 5000:5000 danielhbnl/datavisualization:1.0.0

Now the container is running locally, find the ip on which we can access the container.

On Windows, type ipconfig in the command line and search for the ip of you  internet adapter (you can have multiple, but only one works).
In my case the ip comes from the Wireless LAN adapter Wi-Fi. IPv4 Address: 192.168.2.21.

This IP Address you need to type into the browser followed by :5000. So in my case 192.168.2.21:5000. This will lead you to the website.
