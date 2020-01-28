.PHONY: restconf-check
restconf-check:
	for number in 101 102 103 104 105 106 107 108 109 110 ; do \
		curl -k -u cisco:cisco -H "Accept: application/yang-data+json" https://198.18.1.$$number/restconf/data/native/hostname ; \
	done

.PHONY: pull
pull:
	docker pull dmfigol/jupyter-netdevops:latest

.PHONY: up
up:
	docker kill $(shell docker ps -q); \
	docker pull dmfigol/jupyter-netdevops:latest; \
	docker run -it --rm -d -p 58888:58888 -v ${PWD}/jupyter:/jupyter/ --name=nornir-workshop dmfigol/jupyter-netdevops:latest

.PHONY: start
start:
	docker run -it --rm -p 58888:58888 -v ${PWD}/jupyter:/jupyter/ --name=nornir-workshop dmfigol/jupyter-netdevops:latest

.PHONY: stop
stop:
	docker kill $(shell docker ps -q)

.PHONY: remove-ssh-keys
remove-ssh-keys:
	sed -i "" '/198.18.1/d' ${HOME}/.ssh/known_hosts;

.PHONY: browser
browser:
	open "http://localhost:58888/"; \
    open "http://localhost:58888/notebooks/workshop.ipynb"

.PHONY: credentials
credentials:
	mv session-details.example session-details.txt