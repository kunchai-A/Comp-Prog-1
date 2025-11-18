import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import json
import os

#ส่วนของการประมวลผล

DATA_FILE = 'dpr_data.json'

def save_to_json(new_data, filename):
    data_list = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            if not isinstance(data_list, list): data_list = []
        except json.JSONDecodeError: data_list = []
    
    data_list.append(new_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

#ส่วนของการล้างข้อมูล

def handle_clear_data():
    confirm = messagebox.askyesno(
        "⚠️ Confirm",
        "Are you sure about deleteing all data?\n\n"
        "This process cannot be reversed!",
        icon='warning'
    )
    
    # 2. ถ้าผู้ใช้กด "Yes" (confirm == True)
    if confirm:
        try:
            if os.path.exists(DATA_FILE):
                # 3. สั่งลบไฟล์
                os.remove(DATA_FILE)
                messagebox.showinfo("Finish", "Clear All the data")
            else:
                messagebox.showinfo("Error", "Data Not Found")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
        
        # 4. อัปเดตหน้าจอ (ซึ่งจะแสดงว่า "ไม่พบไฟล์ข้อมูล")
        process_and_display_data()
    else:
        # ถ้าผู้ใช้กด "No"
        messagebox.showinfo("Cancel", "cancel clearing information")

#ส่วนของการค้นหา
def handle_search():
    search_term = entry_search.get().lower()
    if not search_term:
        messagebox.showwarning("Search", "Input")
        return

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        display_report("Not Found")
        return
    
    results = []
    for entry in data_list:
        for value in entry.values():
            if search_term in str(value).lower():
                results.append(entry)
                break
            
    if not results:
        report_string = f"--- Result '{search_term}' ---\n\n"
    else:
        report_string = f"--- Find {len(results)} From '{search_term}' ---\n\n"
        for item in results:
            report_string += json.dumps(item, ensure_ascii=False, indent=2) + "\n"
            report_string += "--------------------\n"
            
    display_report(report_string)

#Helper และ สรุปผล
def display_report(report_string):
    results_area.configure(state='normal')
    results_area.delete(1.0, tk.END)
    results_area.insert(tk.END, report_string)
    results_area.configure(state='disabled')

def process_and_display_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        if not data_list:
            report_string = "None"
        else:
            
            recent_list = data_list[-3:]
            recent_list.reverse() 

            report_string = f"------ Latest 3 Results ------\n\n"
            
            for i, entry in enumerate(recent_list): 
                
                report_string += f"🔹 Result #{i + 1}\n" 
                
                for key, value in entry.items():
                    report_string += f"{key}: {value}\n"
                
                report_string += "----------------------------\n"
    except FileNotFoundError:
        report_string = "No data (data_log_gui.json)\n(Please Try Again)"
    except Exception as e:
        report_string = f"Error: {e}"

    display_report(report_string)
    
#ส่วนบันทึกฟอร์ม
def handle_submit():
    char_name = entry_charname.get()
    char_level = charLevelEntry.get()
    
    try:
        To_hit = int(entryToHit.get())
        mod = int(entryDamageMod.get())
        attack_num = int(AmountOfAttack.get())
        dice_amount = int(entryDiceAmount.get())
        
        # เช็ค Bonus Dice (ถ้าว่างให้เป็น 0)
        dice_amountB_input = entryDiceAmountB.get()
        dice_amountB = int(dice_amountB_input) if dice_amountB_input else 0
        
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter numbers for stats/dice.")
        clear_form()
        return

    dice_type = entryDiceType.get()
    dice_typeB = entryDiceTypeB.get()
    EnemyAc = entryEnemyAc.get()
    Adv = HaveAdv.get()
    CalAdv = Advantage.index(Adv) - 1
    
    # การคำนวณ
    dpr = round(dprcal(dice_type, mod, To_hit, attack_num, dice_amount, dice_amountB, dice_typeB, EnemyAc, CalAdv), 2)
    HitChance = round(HitCh(To_hit, EnemyAc, CalAdv), 2) * 100
    
    if not char_name:
        messagebox.showwarning("Not Enough Data", "Please fill 'char name'")
        return

    form_data = {
        "Name": char_name, "Level": char_level, "DPR": dpr, "Hit Chance": f"{HitChance}%",
        "To Hit": To_hit, "Enemy Armor Class": EnemyAc, "Dice Type": dice_type, "Dice Amount": dice_amount,
        "Damage Mod": mod, "Bonus Dice Type": dice_typeB, "Advantage": Adv,
        "Bonus Dice Amount": dice_amountB, "Amount of Attack": attack_num
    }
    
    save_to_json(form_data, DATA_FILE)
    messagebox.showinfo("Complete", f"Calculated already!")
    clear_form()
    process_and_display_data()

def clear_form():
    entry_charname.delete(0, tk.END)
    charLevelEntry.set(charLevelRange[0])
    entryToHit.delete(0, tk.END)
    entryDiceType.set(diceType[2])
    entryDamageMod.delete(0, tk.END)
    AmountOfAttack.set(AttackAmount[0])
    entryDiceAmount.delete(0, tk.END)
    entryDiceAmountB.delete(0, tk.END)
    entryDiceTypeB.set(diceType[2])
    HaveAdv.set(Advantage[1])
    
#ารคำนวนลูกเต๋า
def dice_output(dice):
    dice = dice.replace("d"," ")
    return int(dice.strip()) # the list will be [amount of dice, value of dice]

def avgdice(dice_type,dice_amount):
    return (int(dice_output(dice_type))+1)*int(dice_amount)/2

def HitCh(tohit,EAC,Adv):
    if Adv == 0: #No adv
        return (21 - int(EAC) + int(tohit))/20
    elif Adv == 1: #have adv
        return 1 - (1-(21 - int(EAC) + int(tohit))/20)**2
    elif Adv == 2: #super adv
        return 1 - (1 - (1-(21 - int(EAC) + int(tohit))/20)**2)**2
    else: #disadv
        return ((21 - int(EAC) + int(tohit))/20)**2

def dprcal(dice_type,mod,to_hit,attack_num,dice_amount,dice_amountB, dice_typeB,EAC,Adv): #Caluated damage per round
    damagePerHit =  avgdice(dice_type,dice_amount) + avgdice(dice_typeB,dice_amountB) + int(mod)
    if HitCh(to_hit,EAC,Adv) >= 1:
        damagePerAttack = damagePerHit
    else:
        damagePerAttack = damagePerHit*HitCh(to_hit,EAC,Adv)
    damagePerRound = damagePerAttack*int(attack_num)
    return damagePerRound

#--------------------------------------------------------------------------------------

#สร้างหน้าต่างหลัก
window = tk.Tk()
window.title("DND Dpr Caluator")
window.geometry("700x800")
window.resizable(False, False)

#Frame 1: ฟอร์ม
form_frame = ttk.Frame(window, padding="20 20 20 10")
form_frame.pack(fill=tk.X)

ttk.Label(form_frame, text="Name: ").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_charname = ttk.Entry(form_frame, width=30)
entry_charname.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Char Level: ").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
charLevelRange = [f"Lv.{i}" for i in range(1,21)]
charLevelEntry = ttk.Combobox(form_frame, values=charLevelRange, width=27, state="readonly")
charLevelEntry.grid(row=0, column=3, padx=5, pady=5)
charLevelEntry.set(charLevelRange[0])

ttk.Label(form_frame, text="To hit: ").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entryToHit = ttk.Entry(form_frame, width=30)
entryToHit.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Advantage: ").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
Advantage = ["Disadvantage","No Advantage", "Advantage", "Super Advantage"]
HaveAdv = ttk.Combobox(form_frame, values=Advantage, width=27, state="readonly")
HaveAdv.grid(row=1, column=3, padx=5, pady=5)
HaveAdv.set(Advantage[1])

ttk.Label(form_frame, text="Amount of Dice: ").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
entryDiceAmount = ttk.Entry(form_frame, width=30)
entryDiceAmount.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Dice Type: ").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
diceType = ["d4", "d6", "d8", "d10", "d12"]
entryDiceType = ttk.Combobox(form_frame, values=diceType, width=27, state="readonly")
entryDiceType.grid(row=2, column=3, padx=5, pady=5)
entryDiceType.set(diceType[2])

ttk.Label(form_frame, text="Damage Mod: ").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
entryDamageMod = ttk.Entry(form_frame, width=30)
entryDamageMod.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Enemy Ac: ").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
E_AC = [f"{i}" for i in range(10,31)]
entryEnemyAc = ttk.Combobox(form_frame, values=E_AC, width=27, state="readonly")
entryEnemyAc.grid(row=3, column=3, padx=5, pady=5)
entryEnemyAc.set(E_AC[0])

ttk.Label(form_frame, text="Amount of Attack: ").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
AttackAmount = [f"{i}" for i in range(1,9)]
AmountOfAttack = ttk.Combobox(form_frame, values=AttackAmount, width=27, state="readonly")
AmountOfAttack.grid(row=4, column=1, padx=5, pady=5)
AmountOfAttack.set(AttackAmount[0])

ttk.Label(form_frame, text="Bonus Damage:").grid(row=5, column=0, columnspan=4, pady=10)

ttk.Label(form_frame, text="Amount of Dice: ").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
entryDiceAmountB = ttk.Entry(form_frame, width=30)
entryDiceAmountB.grid(row=6, column=1, padx=5, pady=5)

ttk.Label(form_frame, text="Dice Type: ").grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
entryDiceTypeB = ttk.Combobox(form_frame, values=diceType, width=27, state="readonly")
entryDiceTypeB.grid(row=6, column=3, padx=5, pady=5)
entryDiceTypeB.set(diceType[2])


submit_button = ttk.Button(form_frame, text="Save", command=handle_submit)
submit_button.grid(row=7, column=0, columnspan=4, pady=10)

#Frame 2: ส่วนค้นหา
search_frame = ttk.Frame(window, padding="20 5 20 10")
search_frame.pack(fill=tk.X)
ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=5)
entry_search = ttk.Entry(search_frame)
entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
search_button = ttk.Button(search_frame, text="Search", command=handle_search)
search_button.pack(side=tk.LEFT, padx=5)

#Frame 3: ส่วนแสดงผลลัพธ์
results_frame = ttk.Frame(window, padding="10 5 10 10")
results_frame.pack(fill=tk.BOTH, expand=True)
ttk.Label(results_frame, text="📊 Result:").pack(anchor=tk.W)
results_area = scrolledtext.ScrolledText(results_frame, height=10, wrap=tk.WORD, state='disabled')
results_area.pack(fill=tk.BOTH, expand=True, pady=5)

#Frame 4: ส่วนปุ่มควบคุม
control_frame = ttk.Frame(window, padding="20 0 20 20")
control_frame.pack(fill=tk.X)

#แสดงข้อมูลที่ได้มาทั้งหมด
summary_button = ttk.Button(control_frame, text="Show 3 Latest Result", command=process_and_display_data)
summary_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

style = ttk.Style(window)
style.configure("Danger.TButton", foreground="red")

#clear ข้อมูล
clear_button = ttk.Button(control_frame, text="Clear", command=handle_clear_data, style="Danger.TButton")
clear_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)

# --- สั่งให้แอปทำงาน ---
process_and_display_data()
window.mainloop()