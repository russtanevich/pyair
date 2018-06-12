

import operators


man = operators.Manager()
disp = operators.Dispatcher(manager=man)


disp.flight(5000, 400)

print man.notifications
