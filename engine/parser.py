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

    if current_scene is not None:
        scenes[current_scene] = buffer
    
    return scenes