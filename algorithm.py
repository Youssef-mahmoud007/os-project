import copy

#srtf
def srtf_preemptive(process_list):

    process_list = copy.deepcopy(process_list)

  
    original_burst = {}
    for p in process_list:
        original_burst[p[2]] = p[0]

    completed = {}
    gantt     = []
    rt_map    = {}      
    t         = 0

    while process_list:
        available = []
        for process in process_list:
            if process[1] <= t:          
                available.append(process)

        if not available:
            gantt.append("Idle")
            t += 1
            continue

        available.sort()                 
        process = available[0]
        pid     = process[2]

        if pid not in rt_map:
            rt_map[pid] = t - process[1]   

        gantt.append(pid)
        t += 1

        updated = list(process)
        updated[0] -= 1                  

        process_list.remove(process)

        if updated[0] == 0:
            ct = t
            at = process[1]
            tt = ct - at                         
            wt = tt - original_burst[pid]        
            completed[pid] = [ct, tt, wt, rt_map[pid]]
        else:
            process_list.append(updated)

    return completed, gantt


#  Round Robin

def round_robin(process_list, time_quanta):

    process_list = copy.deepcopy(process_list)
    process_list.sort()                 

    burst_times = {}
    for p in process_list:
        burst_times[p[2]] = p[1]        

    completed = {}
    gantt     = []
    rt_map    = {}
    t         = 0

    while process_list:
        available = []
        for p in process_list:
            if p[0] <= t:               
                available.append(p)

        if not available:
            gantt.append("Idle")
            t += 1
            continue

        process = available[0]          
        pid     = process[2]

        if pid not in rt_map:
            rt_map[pid] = t - process[0]   

        process_list.remove(process)
        rem_burst = process[1]

        if rem_burst <= time_quanta:
            gantt.extend([pid] * rem_burst)
            t += rem_burst
            ct  = t
            at  = process[0]
            bt  = burst_times[pid]
            tt  = ct - at
            wt  = tt - bt
            completed[pid] = [ct, tt, wt, rt_map[pid]]
        else:

            gantt.extend([pid] * time_quanta)
            t += time_quanta
            process[1] -= time_quanta
            process_list.append(process)

    return completed, gantt



def validate_quantum(raw):
    
    try:
        q = int(raw)
    except (ValueError, TypeError):
        raise ValueError(f"'{raw}' is not an integer.")
    if q <= 0:
        raise ValueError(f"Quantum must be > 0, got {q}.")
    return q


def validate_processes(rows):
   
    if not rows:
        raise ValueError("Add at least one process.")

    rr_list   = []
    srtf_list = []
    seen_pids = set()

    for pid, arrival_s, burst_s in rows:
        pid = pid.strip()
        if not pid:
            raise ValueError("PID cannot be empty.")
        if pid in seen_pids:
            raise ValueError(f"Duplicate PID: '{pid}'.")
        seen_pids.add(pid)

        try:
            arrival = int(arrival_s)
        except ValueError:
            raise ValueError(f"Process '{pid}': arrival time must be an integer.")
        try:
            burst = int(burst_s)
        except ValueError:
            raise ValueError(f"Process '{pid}': burst time must be an integer.")

        if arrival < 0:
            raise ValueError(f"Process '{pid}': arrival time cannot be negative.")
        if burst <= 0:
            raise ValueError(f"Process '{pid}': burst time must be > 0.")

        rr_list.append([arrival, burst, pid])
        srtf_list.append([burst, arrival, pid])

    return rr_list, srtf_list


SCENARIOS = {
    "A – Basic Mixed Workload": {
        "processes": [("P1","0","8"),("P2","1","4"),("P3","2","9"),("P4","3","5")],
        "quantum": "3",
        "note": "Normal workload with varied burst times.",
    },
    "B – Quantum Sensitivity": {
        "processes": [("P1","0","10"),("P2","0","6"),("P3","0","4"),("P4","0","8")],
        "quantum": "2",
        "note": "All arrive together; small quantum makes RR effect very visible.",
    },
    "C – Short-Job-Heavy": {
        "processes": [("P1","0","2"),("P2","0","1"),("P3","1","3"),("P4","2","1"),("P5","3","2")],
        "quantum": "2",
        "note": "Many short jobs — SRTF advantage is very clear here.",
    },
    "D – Interactive Fairness": {
        "processes": [("P1","0","6"),("P2","0","6"),("P3","0","6"),("P4","0","6")],
        "quantum": "2",
        "note": "Equal burst times — tests whether RR distributes first response fairly.",
    },
    "E – Validation Case": {
        "processes": [("P1","0","5"),("P2","1","3")],
        "quantum": "-1",
        "note": "Invalid quantum (-1) — click Run to see validation error.",
    },
    "F – Custom": {
        "processes": [("P1","",""),("P2","",""),("P3","",""),("P4","","")],
        "quantum": "",
        "note": "",
    },
}