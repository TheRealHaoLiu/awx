KIND_CLUSTER_NAME ?= awx-devel
AWX_OPERATOR_DIR ?= awx-operator

## execute make target in awx-operator project directory
.PHONY: awx-operator/%
awx-operator/%:
	@pushd $(AWX_OPERATOR_DIR) > /dev/null && make $(*) && popd > /dev/null

## template kind config file
tmp/kind.conf: tools/kube-dev-kind/kind.conf.template
	@cat tools/kube-dev-kind/kind.conf.template | sed 's|AWX_PROJECT_PATH|$(shell pwd)|g' > tmp/kind.conf

## create kind cluster if does not exist 
kind/create: tmp/kind.conf
	@kind get clusters | grep -q $(KIND_CLUSTER_NAME) || kind create cluster --name $(KIND_CLUSTER_NAME) --config tmp/kind.conf

## delete kind cluster
kind/delete:
	@kind delete cluster --name $(KIND_CLUSTER_NAME)

## export kind kubeconfig to current KUBECONFIG
kind/kubeconfig:
	@kind export kubeconfig --name $(KIND_CLUSTER_NAME)

## deploy awx-operator on kind cluster
kind/deploy/awx-operator:
	@docker tag `$(MAKE) awx-operator/print-IMG` local/ansible/awx-operator:$(GIT_BRANCH)
	@kind load docker-image --name $(KIND_CLUSTER_NAME) local/ansible/awx-operator:$(GIT_BRANCH)
	@$(MAKE) awx-operator/deploy IMG=local/ansible/awx-operator:$(GIT_BRANCH)

## deploy awx development environment on kind cluster
kind/deploy/awx-devel:
	@docker tag $(DEV_DOCKER_TAG_BASE)/awx_kube_devel:$(COMPOSE_TAG) local/ansible/awx_kube_devel:$(GIT_BRANCH)
	@kind load docker-image --name $(KIND_CLUSTER_NAME) local/ansible/awx_kube_devel:$(GIT_BRANCH)
	@ansible-playbook $(AWX_OPERATOR_DIR)/ansible/instantiate-awx-deployment.yml \
        -e development_mode=yes \
        -e image=local/ansible/awx_kube_devel \
        -e image_version=$(GIT_BRANCH) \
        -e image_pull_policy=IfNotPresent \
        -e service_type=nodeport \
        -e namespace=awx

## deploy awx on kind cluster
kind/deploy/awx:
	@docker tag $(DEV_DOCKER_TAG_BASE)/awx:$(COMPOSE_TAG) local/ansible/awx_kube_devel:$(GIT_BRANCH)
	@kind load docker-image --name $(KIND_CLUSTER_NAME) local/ansible/awx_kube_devel:$(GIT_BRANCH)
	@ansible-playbook $(AWX_OPERATOR_DIR)/ansible/instantiate-awx-deployment.yml \
        -e development_mode=yes \
        -e image=local/ansible/awx_kube_devel \
        -e image_version=$(GIT_BRANCH) \
        -e image_pull_policy=IfNotPresent \
        -e service_type=nodeport \
        -e namespace=awx