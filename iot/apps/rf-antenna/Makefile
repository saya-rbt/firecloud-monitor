# Makefile for apps

MODULE = $(shell basename $(shell cd .. && pwd && cd -))
NAME = $(shell basename $(CURDIR))

# Add this to your ~/.vimrc in order to get proper function of :make in vim :
# let $COMPILE_FROM_IDE = 1
ifeq ($(strip $(COMPILE_FROM_IDE)),)
	PRINT_DIRECTORY = --no-print-directory
else
	PRINT_DIRECTORY =
	LANG = C
endif

all:
	@make -C ../.. ${PRINT_DIRECTORY} $@
# .PHONY:

# $(NAME).bin:
# 	@make -C ../.. ${PRINT_DIRECTORY} NAME=$(NAME) apps/$(NAME)/$@

# emergency:

# sensors:
# 	@make -C ../.. ${PRINT_DIRECTORY} $@
# 
# clean mrproper:
# 	@make -C ../.. ${PRINT_DIRECTORY} $@

