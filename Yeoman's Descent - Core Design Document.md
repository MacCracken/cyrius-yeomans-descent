# **Yeoman's Descent: Core Design & Technical Specification**

## **1\. High-Level Concept**

**Yeoman’s Descent** is a classic text-based Multi-User Dungeon (MUD) set in a gritty techno-feudal universe. Players begin as low-ranking serfs or squires and must delve into the "Under-Grid"—a massive, subterranean arcology of ruined servers, rusted automated defenses, and rogue AI fiefdoms. The game relies entirely on text parsing, ANSI color aesthetics, and deep, imaginative world-building, accurately reflecting the DikuMUD and LPMud era of the late 1980s to mid-1990s.

* **Target Slate:** Summer of Games internal testing  
* **Engine & Backend:** Cyrius-native TCP socket server  
* **State Management:** T.Ron (handling transactional memory and persistent player states)  
* **Game Management Interface:** Handled via Joshua

## **2\. Combat System & Mechanics**

To ensure the genuine 90s text-MUD feel, combat avoids deterministic, MMO-style cooldowns in favor of **hidden dice rolls** running under the hood on a strict server-wide "tick" system. The math leans heavily on classic tabletop RPG paradigms adapted for digital speed.

### **2.1 The Tick Architecture**

Combat resolves automatically once engaged (via the kill \[target\] command). The server calculates one combat round every **2.5 seconds (the Combat Tick)**. During this tick, both the player and the target execute their attacks, and the parser translates the math into dynamic text output.

### **2.2 Base Attributes**

* **STR (Strength):** Modifies physical damage and carrying capacity (weight limits were vital in classic MUDs).  
* **DEX (Dexterity):** Increases evasion chance and strike accuracy.  
* **CON (Constitution):** Determines maximum HP and stamina regeneration rates.  
* **TEC (Tech / Intelligence):** Powers Splicer/Chaplain abilities and energy weapon scaling.

### **2.3 Combat Math Formula**

Behind the scenes, the server generates simulated dice rolls:

* **Hit Calculation:** 1d20 \+ DEX Modifier \+ Weapon Accuracy vs. Target Armor Class (AC). (A traditional THAC0 style system, where lower armor class numbers provide better defense).  
* **Damage Roll:** Each weapon has a dice profile (e.g., a Shock-Pike is 2d6). Total damage \= Weapon Dice \+ STR or TEC Modifier.

// Example Combat Output Stream  
\> kill drone  
You charge the deactivated security drone\!  
\[Tick 1\] You swing your shock-pike... and CRUSH the drone\! (12 dmg)  
\[Tick 1\] The security drone fires a rusted laser... but misses you entirely.  
\[Tick 2\] You thrust your shock-pike... grazing the drone. (4 dmg)  
\[Tick 2\] The security drone's rusted laser SEARS your left arm\! (8 dmg)

## **3\. Class Structure**

| Class | Role | Core Commands | Attribute Focus   |
| :---- | :---- | :---- | :---- |
| Pikeman | Tank / Melee | bash, brace, cleave | STR / CON |
| Splicer | Caster / Hacker | hack, overload, emp | TEC |
| Courier | Rogue / Stealth | sneak, backstab, bypass | DEX |
| Chaplain | Healer / Support | patch, stim, rally | TEC / CON |

## **4\. The Core Loop & Gameplay**

1. **Exploration:** Players navigate via cardinal directions (n, s, e, w, u, d). Rooms feature rich textual descriptions detailing the decaying architecture, exits, and present entities.  
2. **Combat & Looting:** Players engage hostiles to acquire raw materials, rusted tech components, and credits. Loot must be manually retrieved via commands like get all from corpse.  
3. **Rest & Recovery:** Endurance and Health regenerate over time, but players must locate safe rooms (Hubs/Taverns) and use the rest or sleep commands to recover effectively, creating natural social gathering points.  
4. **Territory (Guilds):** High-level play involves aligning with tech-fiefdoms to secure and hold zones within the Descent.

## **5\. Technical Architecture**

The backend must replicate the Telnet era while benefiting from modern stability.

* **Telnet Protocol:** Players connect via raw TCP sockets using standard clients (Mudlet, CMUD) or a browser-based Telnet wrapper.  
* **Verb-Noun Parser:** A robust NLP-lite parser designed to interpret complex string commands (e.g., give monoblade to kiran or put all.rations in backpack).  
* **Zones & Resets:** The game world is compartmentalized into Zones. A routine "Zone Reset" triggers every 15-30 minutes, respawning mobs and loot, but only if the room currently contains no active players.