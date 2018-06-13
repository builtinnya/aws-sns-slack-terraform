.PHONY: build test clean

clean:
	find . -type d -name "_build" | xargs rm -fr
	find . -type d -name "test_results" | xargs rm -fr

build: clean
	./build-function.sh $(OUTDIR)

test:
	$(MAKE) -C sns-to-slack/ test
