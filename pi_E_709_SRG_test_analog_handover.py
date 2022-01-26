import numpy as np
import pi_E_709_SRG
import ni_PCIe_6738

# init:
ao_piezo_channel = 0
ao = ni_PCIe_6738.DAQ(num_channels=1, rate=1e5, verbose=False)
piezo = pi_E_709_SRG.Controller('COM10', 0 , 500, verbose=True)

# configure:
num_moves = 11
ao_play_seconds = 0.2
random = True
z_min, z_max = piezo.z_min, piezo.z_max
piezo.set_analog_control_limits(0, 10, z_min, z_max) # 0 -> 10 = best control
moves = np.linspace(z_min, z_max, num_moves)
if random: moves = np.random.uniform(z_min, z_max, num_moves)

# run:
print('\n Testing servo to analog control handover:')
total_change_nm = 0
for move_um in moves:
    # servo move:
    piezo.move_um(move_um, relative=False)
    z_servo = piezo.get_position(verbose=False)
    # analog control:
    z_voltage = piezo.get_voltage_for_move_um(0)        # ~zero motion voltage
    ao_volts = np.zeros((ao.s2p(ao_play_seconds), ao.num_channels), 'float64')
    ao_volts[:, ao_piezo_channel] = z_voltage           # make voltage array
    piezo.set_analog_control_enable(True)               # switch to analog
    ao.play_voltages(ao_volts, force_final_zeros=False) # play
    z_analog = piezo.get_position(verbose=False)
    # back to servo control:
    piezo.set_analog_control_enable(False)
    z_final = piezo.get_position(verbose=False)
    # results:
    print('z change servo ->analog = ', 1e3 * round(z_servo - z_analog, 3))
    print('z change analog->servo  = ', 1e3 * round(z_analog - z_final, 3))
    print(' Total change for move (nm) = ', 1e3 * round(z_servo - z_final, 3))
    total_change_nm += 1e3 * round(z_servo - z_final, 3)
print('\n Average change per move (nm) = ', total_change_nm / num_moves)

# tidy up:
piezo.move_um(0, relative=False)
piezo.close()
ao.close()
