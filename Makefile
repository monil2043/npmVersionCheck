# You can set these variables from the command line.
PYTHON       = python3
VENVDIR      = ./venv
REQUIREMENTS = requirements.txt
STAGE = dev


#######################################################
# HANDLE PYTHON VIRTUAL ENV
#######################################################
.PHONY: venv
venv:
	@if [ -d ${VENVDIR} ] ; then \
		echo "venv already exists."; \
		echo "To recreate it, remove it first with \`make clean-venv'."; \
	else \
		${PYTHON} -m venv ${VENVDIR}; \
		${VENVDIR}/bin/python3 -m pip install --upgrade pip; \
		${VENVDIR}/bin/python3 -m pip install -r ${REQUIREMENTS}; \
		echo "The venv has been created in the ${VENVDIR} directory"; \
	fi


deploy:
	cdk deploy --require-approval=never --profile ${AWS_PROFILE}

destroy:
	cdk destroy --force

format:
	yapf -d -vv --style=./.style -r .

unit:
	# cp -r layers/mercuryReusableMethods venv/lib/python3.12/site-packages/
	pytest tests/unit --cov=. --cov-report xml



#######################################################
# CLEAN DIRECTORIES BEFORE COMMITTING TO SOURCE CONTROL
#######################################################
.PHONY: clean
clean: clean-python clean-venv
	rm -rf .venv || true
	rm -rf __pycache__ || true
    # rm -rf cdk.staging
	rm -rf cdk.out
    # rm -rf .coverage

.PHONY: clean-venv
clean-venv:
	rm -rf ${VENVDIR}

.PHONY: clean-python
clean-python:
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '.coverage' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.tox' -exec rm -fr {} +
	find . -name '__pycache__' -exec rm -fr {} +