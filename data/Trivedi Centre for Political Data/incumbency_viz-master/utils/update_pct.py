from csv_gen import main as update_assembly_data
from update_pids import main as update_pid_data

update_pid_data()
print("-" * 80)
print("[UPDATED] PID data")
print("-" * 80)
update_assembly_data()