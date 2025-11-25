def parse_story(path: str):
    scenes = {}
    current_scene = None
    buffer = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # SCENE
            if line.startswith("\\scene"):
                if current_scene:
                    scenes[current_scene] = buffer
                parts = line.split()
                current_scene = parts[1]
                buffer = []
                continue
            # CLEAR SCREEN 
            if line.startswith("\\clear"):
                buffer.append({"type": "clear"})
                continue
                
            # DIVIDER  
            if line.startswith("\\divider"):
                parts = line.split(" ", 1)
                symbol = parts[1] if len(parts) > 1 else "="
                buffer.append({"type": "divider", "symbol": symbol})
                continue
            
            # PAUSE 
            if line.startswith("\\pause"):
                parts = line.split(" ", 1)
                message = parts[1] if len(parts) > 1 else "\nTekan Enter untuk melanjutkan..."
                buffer.append({"type": "pause", "message": message})
                continue

            # PROGRESS BAR 
            if line.startswith("\\progress"):
                parts = line.split(" ", 2)
                duration = float(parts[1]) if len(parts) > 1 else 2
                label = parts[2] if len(parts) > 2 else "Memproses"
                buffer.append({"type": "progress", "duration": duration, "label": label})
                continue
            
            # LOADING 
            if line.startswith("\\loading"):
                parts = line.split(" ", 2)
                duration = float(parts[1]) if len(parts) > 1 else 2
                message = parts[2] if len(parts) > 2 else "Loading"
                buffer.append({"type": "loading", "duration": duration, "message": message})
                continue
            
            # CHOICE - FIXED PARSING
            if line.startswith("\\choice"):
                # format: \choice "Teks Pilihan" goto target_scene
                try:
                    # Extract text dalam quotes
                    text_start = line.find('"')
                    text_end = line.find('"', text_start + 1)
                    if text_start != -1 and text_end != -1:
                        choice_text = line[text_start + 1:text_end]
                        # Extract target setelah "goto"
                        goto_pos = line.find("goto", text_end)
                        if goto_pos != -1:
                            target_scene = line[goto_pos + 4:].strip()
                            buffer.append({
                                "type": "choice", 
                                "text": choice_text, 
                                "target": target_scene
                            })
                except Exception as e:
                    print(f"Error parsing choice: {line} - {e}")
                continue
            
            # GO TO
            if line.startswith("\\goto"):
                parts = line.split()
                if len(parts) >= 2:
                    buffer.append({"type": "goto", "target": parts[1]})
                continue
            
            # BOLD
            if line.startswith("\\bold"):
                inside = line.replace("\\bold", "").strip()
                inside = inside.strip('"')
                buffer.append({"type": "bold", "text": inside})
                continue

            # COLOR
            if line.startswith("$"):
                parts = line.split(" ", 1)
                color = parts[0][1:]
                text = parts[1] if len(parts) > 1 else ""
                buffer.append({"type": "color", "color": color, "text": text})
                continue

            # TEKS BIASA
            if current_scene and line.strip():
                buffer.append({"type": "text", "text": line})
            
            # Tambahkan di bagian parsing
            if line.startswith("\\battle"):
                # Format: \battle player_hp=100 enemy_hp=100 player_name="Kamu" enemy_name="Hantu"
                config = {}
                parts = line.split()
                
                for part in parts[1:]:  # Skip \battle
                    if '=' in part:
                        key, value = part.split('=', 1)
                        # Handle string values dengan quotes
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        # Convert numeric values
                        elif value.isdigit():
                            value = int(value)
                        config[key] = value
                
                buffer.append({"type": "battle", "config": config})
                continue
            
    if current_scene is not None:
        scenes[current_scene] = buffer
    
    return scenes