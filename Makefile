all: doxy fly.log

fly.log: fly.py fly.fly
	python $^ > $@ && tail $(TAIL) $@
	
doxy:
	rm -rf docs ; doxygen doxy.gen 1>/dev/null
	