#!/bin/bash
if [ ! -d /ml4scm/src/ml4scm ]; then
	echo "Must mount the ml4scm project root directory as '/ml4scm' when launching docker" 1>&2
	exit 1
fi

monitor() {
	cd /ml4scm/
	export ENTR_INOTIFY_WORKAROUND=true
	while sleep 0.5; do
 		git ls-files --cached --modified --other --exclude-standard \
 			| sort -u \
 			| tr '\n' '\0' \
 			| xargs -0 realpath \
 			| entr -anrd /bin/sh -c 'python3 setup.py install >/dev/null 2>&1 && echo "$(date): reinstalled ml4scm"'
	done
}

cd /ml4scm/
python3 setup.py install
monitor &
/usr/local/bin/jupyter-notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
