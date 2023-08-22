#!/bin/bash 
source ~/.bashrc
imageVersion="latest"
repository_name="load_test_server"
imageTag=$repository_name:$imageVersion
# aws_account_id=${aws_account_id:-000000000000000}
repositoryLinkPrefix="" #"$aws_account_id.dkr.ecr.ap-south-1.amazonaws.com"
imagePushTag=""
imagePushTagSuffix="ltserver"

if [ "$repository_name" == "" ];then
	echo "Repository name / project name not given."
	exit
fi

rm -rf $repository_name.zip

pushd  ..

	sha=`git log -1 --pretty=format:%h`
	sha_status=$?

	if [ $sha_status -ne 0 ];then
		echo "Unable to get SHA assuming latest"
		sha="latest"
	fi

	echo $sha > $repository_name-$imagePushTagSuffix.sha
	imageVersion=$imageVersion_$sha
	rm -rf $repository_name.zip
	zip -r --exclude=event-logger-js-client* --exclude=tempFiles* --exclude=*.db --exclude=*.git* --exclude=*docker* --exclude=*venv* --exclude=*pyenv* --exclude=*logs* --exclude=*keys* --exclude=*__pycache__* --exclude=*py.swp* $repository_name.zip ./
	
	cp $repository_name.zip ./docker

popd

sed "s/<zipname>/$repository_name/g" Dockerfile.og > Dockerfile

docker build -t $imageTag .
image_build_status=$?

# echo "Image Build Status "$image_build_status

if [ "$image_build_status" != 0 ];then
	echo "Build Failed."
	exit
else
	echo "Docker build completed."
fi

if [ "$repositoryLinkPrefix" != "" ];then
	rname=$repositoryLinkPrefix"/"$repository_name
	imagePushTag=$rname:$imageVersion-$imagePushTagSuffix
	echo "You can push the docker using: $imagePushTag"
	docker tag $imageTag $imagePushTag
	docker push $imagePushTag
	docker tag $imagePushTag $rname:latest
	docker push $rname:latest

fi