PMC Retrieval 
========================

TODO Complete description

========================

1.- Clone this repository 

    $ git clone https://github.com/javicorvi/pmc_retrieval.git
    
2.- Python 2.7 
	
	
3.- Third Party 


	
4.- Run the script
	
	To run the script just execute python pmc_retrieval -o /home/myname/pmc_retrieval 

5.- The container 
	
	If you just want to run the app without any kind of configuration you can do it 
	through the docker container is avaiblable in https://hub.docker.com/r/javidocker/pmc_retrieval/ 

	To run the docker: 
	
	docker run --rm -u $UID  -v /home/yourname/pubmed_data:/app/data pmc_retrieval

	the path home/yourname/pubmed_data will be the working directory in where the data will be downloaded.