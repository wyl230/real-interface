docker build -f ./Dockerfile -t test:1.0 .
docker run -it test:1.0 -p 5001:5002 -p 1883:1883

# 当您在Dockerfile中使用EXPOSE指令暴露了容器的端口时，这只是说明该端口应该被映射，以便它可以在容器外部访问。
# 要映射这些端口，您可以使用docker run命令中的-p参数。对于暴露的两个端口，您可以使用类似于以下命令的参数：
# 📎
# docker run -p 8080:80 -p 5000:5000 myimage
# 这将运行myimage镜像，并将容器内部的80端口映射到主机的8080端口，将容器内部的5000端口映射到主机的5000端口。
# 如果你需要启动的命令是一个web服务或者一个长时间运行，你可以使用docker run命令中的-d参数将容器在后台运行：
# 📎
# docker run -d -p 8080:80 -p 5000:5000 myimage
# 这将在后台运行一个名为mycontainer的容器，并将80和5000端口映射到主机的8080和5000端口。
