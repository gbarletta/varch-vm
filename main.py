import machine

vm = machine.Machine(4096)
vm.load_file("hello.bin", 0x0)
vm.run(pc=142, debug=True)