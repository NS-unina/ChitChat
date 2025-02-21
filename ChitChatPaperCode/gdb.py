import re
import subprocess
import ctypes
from sys import argv



# # deprecata
def run_gdb_distances_var(program_path, nome_f, nomi_var):
    # Comando per avviare GDB con il programma esterno
    cmd = ['gdb', '-q', program_path]  # '-q' per GDB in modalità silenziosa

    cmd += ['-ex', 'break ' + nome_f]
    cmd += ['-ex', 'run']
    for elemento in nomi_var[nome_f]:
        cmd += ['-ex', 'print &' + elemento]

    # Esegui il comando con subprocess
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Interagisci con GDB, inviando i comandi uno alla volta
    process.stdin.write("quit\n")
    process.stdin.flush()

    # Leggi l'output e gli errori di GDB
    stdout, stderr = process.communicate()
    
    pattern = r'\$[\d]+ =.*?(0x[0-9a-fA-F]+)'

    matches = re.findall(pattern, stdout)
    indirizzi = []
    distanze = []
    for indirizzo in matches:
        if len(indirizzo) > 10:
            stringa_troncata = "0x" + indirizzo[-8:]
            indirizzi.append(stringa_troncata)
        elif len(indirizzo) < 10:
            riempimento = 10 - len(indirizzo)
            parte1 = "0" * riempimento
            finale = indirizzo[:2] + parte1 + indirizzo[2:]
            indirizzi.append(finale)
        else: 
            indirizzi.append(indirizzo)
    return_address = run_gdb_return(program_path, nome_f)
    for indirizzo in indirizzi:
        distanza = hex(int(return_address, 16) - int(indirizzo, 16))
        
        distanze.append(distanza)
        
    return distanze


# deprecata            
def run_gdb_return(program_path, nome_f):
    # Comando per avviare GDB con il programma esterno
    cmd = ['gdb', '-q', program_path]  # '-q' per GDB in modalità silenziosa
    cmd += ['-ex', 'run']
    cmd += ['-ex', 'set args a a a']
    cmd += ['-ex', 'break ' + nome_f]
    cmd += ['-ex', 'run']
    cmd += ['-ex', 'info frame']

    # Esegui il comando con subprocess
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Interagisci con GDB, inviando i comandi uno alla volta
    process.stdin.write("quit\n")
    process.stdin.flush()

    # Leggi l'output e gli errori di GDB
    stdout, stderr = process.communicate()
    
    # pattern = r'rip at (0x[0-9a-fA-F]+)'
    pattern = r'ip at (0x[0-9a-fA-F]+)'

    matches = re.findall(pattern, stdout)

    if matches:
        indirizzo = matches[0]
    #     if len(indirizzo) > 10:
    #         stringa_troncata = "0x" + indirizzo[-8:]
    #         return stringa_troncata
    #     elif len(indirizzo) < 10:
    #         riempimento = 10 - len(indirizzo)
    #         parte1 = "0" * riempimento
    #         finale = indirizzo[:2] + parte1 + indirizzo[2:]
    #         return finale
    #     else: 
    #         return indirizzo
    # else: 
    #     return "indirizzo di ritorno non trovato"
        address_int = int(indirizzo, 16)
        
        # Formattta l'intero in esadecimale a 32 bit con 8 cifre (zero-padding)
        return f"0x{address_int:08x}"
    else: 
        return "indirizzo di ritorno non trovato"           

    
    
    
#deprecata 
def process_file(path_file):
    nomi_f_not_exe = []
    nomi_f_exe = []
    nomi_var = {}
    file = open(path_file, 'r', encoding='utf-8')
    riga = ""
    while(True):
        riga = file.readline().strip()
        if riga == "FINE":
            break
        if(riga == "FUNZIONE NOT EXE"):
            riga = file.readline().strip()
            new_f = riga
            nomi_f_not_exe.append(riga)
            riga = file.readline().strip()
            while(riga != "FINE FUNZIONE NOT EXE"):
                nomi_var.setdefault(new_f, []).append(riga)
                riga = file.readline().strip()
        elif(riga == "FUNZIONE EXE"):
            riga = file.readline().strip()
            new_f = riga
            nomi_f_exe.append(riga)
            riga = file.readline().strip()
            while(riga != "FINE FUNZIONE EXE"):
                nomi_var.setdefault(new_f, []).append(riga)
                riga = file.readline().strip()
    return nomi_f_not_exe, nomi_f_exe, nomi_var






    
#funzione che permette di ottenere l'indirizzo di una funzione all'interno di un programma
def run_gdb_address_f(program_path, nome_f):
    
    # Comando per avviare GDB con il programma esterno
    cmd = ['gdb', '-q', program_path]  # '-q' per GDB in modalità silenziosa
    cmd += ['gdb','break ' + nome_f]
    cmd += ['-ex', 'run']
    cmd += ['-ex', '  ' + nome_f]
    #cmd += ['-ex', 'info functions']

    #fix by mario:
    cmd = [
        "gdb", "-q", program_path,   # Avvia GDB in modalità silenziosa (-q)
        # "-ex", "set print address on",  # Mostra gli indirizzi in modo chiaro
        "-ex", "run",                # Esegui il programma
        "-ex", f"break {nome_f}",    # Imposta un breakpoint sulla funzione
        "-ex", "run",                # Esegui il programma
        "-ex", f"disassemble {nome_f}",  # Mostra il disassemblato della funzione
        "-ex", "quit"                # Esci da GDB
    ]
    
    # Esegui il comando con subprocess
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Interagisci con GDB, inviando i comandi uno alla volta
    process.stdin.write("quit\n")
    process.stdin.flush()

    # Leggi l'output e gli errori di GDB
    stdout, stderr = process.communicate()
    # print(stdout)    
    # Stampa l'output di GDB)
    tokens = stdout.split()

    # Cerca il token che inizia con "0x"
    sottostringa = next((token for token in tokens if token.startswith("0x")), None)

    sottostringa = sottostringa.rstrip('.')
    if ":" in sottostringa:
        sottostringa = sottostringa.replace(":","")
    # if len(sottostringa) > 10:
    #     stringa_troncata = "0x" + sottostringa[-8:]
    #     return stringa_troncata
    # elif len(sottostringa) < 10:
    #     riempimento = 10 - len(sottostringa)
    #     parte1 = "0" * riempimento
    #     # parte1="" # voglio che l'indirizzo estratto da gdb sia come sia es 0x1191 piuttosto che 0x0001191 (perchè voglio si aindipendente da 64 o 32 bit)
    #     finale = sottostringa[:2] + parte1 + sottostringa[2:]
    #     return finale
    # else:
    #     return sottostringa
    address_int = int(sottostringa, 16)
    
    # Formattta l'intero in esadecimale a 32 bit con 8 cifre (zero-padding)
    return f"0x{address_int:08x}"
        

    
#Funzione che calcola la distanza tra una variabile e il return address di una funzione, restituisce un intero
def run_gdb_distanza_var(program_path, nome_f, distanza_var_f):
    cmd = ['gdb', '-q', program_path]  # '-q' per GDB in modalità silenziosa

    cmd += ['-ex', 'break ' + nome_f]
    cmd += ['-ex', 'run']
    cmd += ['-ex', 'print &' + distanza_var_f[nome_f]]

    #fix by mario
    # Prepare the GDB command using the desired syntax
    cmd = [
        "gdb", "-q", program_path,  # Avvia GDB in modalità silenziosa (-q)
        "-ex", "run",              # Esegui il programma
        "-ex", "set args a a a",              # setta argv (il primo parametro è di interesse)
        "-ex", f"break {nome_f}",  # Imposta il breakpoint nella funzione nome_f
        "-ex", "run",              # Esegui il programma
        "-ex", f"print &{distanza_var_f[nome_f]}",  # Stampa l'indirizzo della variabile
    ]
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Interagisci con GDB, inviando i comandi uno alla volta
    process.stdin.write("quit\n")
    process.stdin.flush()

    # Leggi l'output e gli errori di GDB
    stdout, stderr = process.communicate()
    
    pattern = r'\$[\d]+ =.*?(0x[0-9a-fA-F]+)'

    match = re.search(pattern, stdout)   
    indirizzo = match.group(1)
    preprocess = ""
    if len(indirizzo) > 10:
        preprocess = "0x" + indirizzo[-8:]
    elif len(indirizzo) < 10:
        riempimento = 10 - len(indirizzo)
        parte1 = "0" * riempimento
        preprocess = indirizzo[:2] + parte1 + indirizzo[2:]
    else:
        preprocess = indirizzo
    return_address= run_gdb_return(program_path, nome_f)

    
    distanza = int(return_address, 16) - int(preprocess, 16)
    return distanza
         
            
            
            
#Funzione che calcola la distranza tra 2 variabili in una specifica funzione, restituisce un dizionario la cui chiave  è il nome della funzione e il cui valore è la distanza tra le due variabili
def run_gdb_distanza_var_var(program_path, nome_f, distanza_var_var):
    cmd = ['gdb', '-q', program_path]  # '-q' per GDB in modalità silenziosa
    cmd += ['-ex', 'run']
    cmd += ['-ex', 'set args a a a']
    cmd += ['-ex', 'break ' + nome_f]
    cmd += ['-ex', 'run']
    cmd += ['-ex', 'print &' + distanza_var_var[nome_f][0]]
    cmd += ['-ex', 'print &' + distanza_var_var[nome_f][1]]


    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Interagisci con GDB, inviando i comandi uno alla volta
    process.stdin.write("quit\n")
    process.stdin.flush()

    # Leggi l'output e gli errori di GDB
    stdout, stderr = process.communicate()
    
    pattern = r'\$[\d]+ =.*?(0x[0-9a-fA-F]+)'

    matches = re.findall(pattern, stdout)   
    indirizzi = []
    for indirizzo in matches:
        if len(indirizzo) > 10:
            stringa_troncata = "0x" + indirizzo[-8:]
            indirizzi.append(stringa_troncata)
        elif len(indirizzo) < 10:
            riempimento = 10 - len(indirizzo)
            parte1 = "0" * riempimento
            finale = indirizzo[:2] + parte1 + indirizzo[2:]
            indirizzi.append(finale)
        else: 
            indirizzi.append(indirizzo)
    indirizzo1 = indirizzi[0]
    indirizzo2 = indirizzi[1]
    if ((int(indirizzo1, 16) - int(indirizzo2, 16)>0)):
        return int(indirizzo1, 16) - int(indirizzo2, 16)
    else:
        return int(indirizzo2, 16) - int(indirizzo1, 16)
            

    
#Funzione che estrae la base della libc in cui si trova la stringa binsh        
def base_libc(program_path):
    # Comando da eseguire
    comando = "ldd " + program_path
    process = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    pattern = r'libc\.so\.6 => /lib/x86_64-linux-gnu/libc\.so\.6 \((0x[0-9a-fA-F]+)\)'

    matches = re.search(pattern, stdout)
    if matches:
        indirizzo = matches.group(1)
        if len(indirizzo) > 10:
            stringa_troncata = "0x" + indirizzo[-8:]
            return stringa_troncata
        elif len(indirizzo) < 10:
            riempimento = 10 - len(indirizzo)
            parte1 = "0" * riempimento
            finale = indirizzo[:2] + parte1 + indirizzo[2:]
            return finale
        else: 
            return indirizzo
    else:
        print("Nessun indirizzo trovato.")
    
# Funzione che calcola l'offset rispetto alla base libc in cui si trova la stringa binsh
def offset_binsh():
    # Comando da eseguire    
    comando = "strings -a -t x /lib/x86_64-linux-gnu/libc.so.6 | grep '/bin/sh'"
    process = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    parti = stdout.split()
    offset =  parti[0]
    if len(offset) < 8:
        riempimento = 8 - len(offset)
        new_offset = "0x" + "0"*riempimento + offset
        return new_offset
    else:
        return "0x" + offset
        
#Funzione che calcola e restituisce l'indirizzo della stringa binsh nel sistema
def compute_binsh(path_eseguibile):
    b_libc = int(base_libc("./" + path_eseguibile), 16)
    of_binsh = int(offset_binsh(), 16)
    somma = b_libc + of_binsh
    indirizzo_binsh = hex(somma)
    return indirizzo_binsh
        
#Funzione che restituisce l'indirizzo in memoria della system()
def system_address():
    
    libc = ctypes.CDLL('libc.so.6')
    indirizzo_system_byte = libc.system
    indirizzo_system = str(indirizzo_system_byte)
    pattern = r"0x[0-9a-fA-F]+"  # Pattern per trovare indirizzi esadecimali

    match = re.search(pattern, indirizzo_system)

    if match:
        indirizzo = match.group()
        if len(indirizzo) > 10:
            stringa_troncata = "0x" + indirizzo[-8:]
            return stringa_troncata
        elif len(indirizzo) < 10:
            riempimento = 10 - len(indirizzo)
            parte1 = "0" * riempimento
            finale = indirizzo[:2] + parte1 + indirizzo[2:]
            return finale
        else: 
            return indirizzo
        
    else:
        return "errore nel trovare indirizzo system"

# Funzione che verifica se nel file input è richiesta la funzione system()    
def system_required(path_file):
    file = open(path_file, 'r', encoding='utf-8')
    riga = ""
    while(True):
        riga = file.readline().strip()
        if riga == "FINE":
            return "NO"
        if(riga == "SYSTEM ADDRESS()"):
            return "YES"  
        
# Funzione che verifica se nel file input è richiesta la stringa binsh       
def binsh_required(path_file):
    file = open(path_file, 'r', encoding='utf-8')
    riga = ""
    while(True):
        riga = file.readline().strip()
        if riga == "FINE":
            return "NO"
        if(riga == "BINSH ADDRESS"):
            return "YES"  
    
    




#funzione che estrae i nomi  simbolici di interesse dal file di testo
def process_file2(path_file):
    nome_funzione_target = ""
    distanza_var_f = {}
    distanza_var_var = {}
    file = open(path_file, 'r', encoding='utf-8')
    riga = ""
    while(True):
        riga = file.readline().strip()
        if riga == "FINE":
            break
        if(riga == "FUNZIONE TARGET ADDRESS"):
            riga = file.readline().strip()
            nome_funzione_target = riga
            
        elif(riga == "DISTANZA TRA VARIABILE E FUNZIONE"):
            nome_f = file.readline().strip()
            nome_var = file.readline().strip()
            distanza_var_f[nome_f] = nome_var
            
        elif(riga == "DISTANZA TRA VARIABILI"):
            nome_f = file.readline().strip()
            nome_var1 = file.readline().strip()
            nome_var2 = file.readline().strip()
            distanza_var_var.setdefault(nome_f, []).append(nome_var1)
            distanza_var_var.setdefault(nome_f, []).append(nome_var2)
    return nome_funzione_target, distanza_var_f, distanza_var_var
            
            


#address_f_exe e return address hanno corrispondenza 1 a 1 con nomi_f_exe, address_f_not_exe ha corrispondenza 1 a 1 con address_f_not_exe
#distance_var ha corrispondenza 1 a 1 con nomi_var
#solo le funzioni exe che hanno variabili saranno presenti in nomi_val

def main(path_file, path_eseguibile):
    nome_funzione_target = ""
    distanza_var_f = {}
    distanza_var_var = {}
    val_distanza_var_f = {}
    val_distanza_var_var = {}
    indirizzo_f_target = ""
    indirizzo_system = ""
    indirizzo_binsh = ""
    nome_funzione_target, distanza_var_f, distanza_var_var = process_file2(path_file)
    if(nome_funzione_target != ""):
        indirizzo_f_target = run_gdb_address_f(path_eseguibile, nome_funzione_target)
    if(len(distanza_var_f) != 0):
        for key in distanza_var_f.keys():
            val_distanza_var_f[key] = run_gdb_distanza_var(path_eseguibile, key, distanza_var_f)
    if(len(distanza_var_var) != 0):
        for key in distanza_var_var.keys():
            val_distanza_var_var[key] = run_gdb_distanza_var_var(path_eseguibile, key, distanza_var_var)
    
    if(system_required(path_file) == "YES"):
        indirizzo_system = system_address()
    if(binsh_required(path_file) == "YES"):
        indirizzo_binsh = compute_binsh(path_eseguibile)
    return nome_funzione_target, distanza_var_f, val_distanza_var_f, val_distanza_var_var, indirizzo_f_target, indirizzo_system, indirizzo_binsh, distanza_var_var 


    
    
      
# if __name__ == "__main__":
#     main(argv[1], argv[2])
                 
#gdb_commands = 'info functions'
#run_gdb(program_path, gdb_commands)
