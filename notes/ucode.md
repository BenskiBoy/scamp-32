# Notes
In the original scamp-cpu, each instruction fetch from memory would retrieve a 16 bit instruction which could also contain a value. This value could either represent i8H or i8L depending on the instruction.
i8H/L meant that bits 0-7 would contain the value but the top 8 bits (8-15) would either be all high or low respectively.
i8H was used for accessing registers as they were mapped to the top 256 memory locations (i.e. 0xFF00 -> 0xFFFF).
where as i8l was used a 8 bit commands for values to manipulate.

i8H was also also used specifically for some instructions such as `add x, i8H`, presumably this was useful for adding small negative constants (-256->-1)

If a 16 bit value was needed (such as for a memory pointer or just wanting to use a 16 bit value), the ucode steps would just load the current PC reg into the address register, fetch the value and do what it needed to do.

IOLH?

Now we have 32 bits at our disposal, things change slightly, but not too much.
Still want to have registers available. Naturally we could address these regsiters using the 32 bits but that's wasteful!
We can similarly have a IOH command so that we just throw all higher bits high using a 8 bit variable to address the registers, maintaining much of the existing logic.
Worth noting not all address space is mapped, but that's fine, we can just throw those high as well.

We might start to wonder about commands like i8L/i16L/i16H and while this may be helpful as mentioned above for arithmatic of negative numbers, 
    a) We're trying to stay within 256 instructions, and after creating different varients of instructions we'll lose space
    b) We now have easier control of fetching specific variable lengths thanks to our memory control managemnt

So in summary,
- We still need our instruction register regardless
- the initial 2 micro steps of every instruction (PO AI, MO II P+) will change to (PO AI, MO16 II P+2) so we can save steps on register commands
- IOH will set data bits 8-31 high
- IOL no longer necessary


@BEN!!! This won't work. if you get inst and then the next value will be offset, how would you fetch a 32 variable next???

initial opcode needs to be MO8 II P+. 
Could make IOH MO8H!!! Then instruction register is only 8 bits, 