fly.log: fly.py fly.fly
	python $^ > $@ && tail $(TAIL) $@