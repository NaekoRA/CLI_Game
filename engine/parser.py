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
            
            # Battle command dengan branching
            if line.startswith("\\battle"):
                config = {}
                branches = {}
                parts = line.split()
                
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        # Handle branch targets
                        if key in ['win', 'lose', 'draw', 'surrender']:
                            branches[key] = value
                        else:
                            # Handle config values
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.isdigit():
                                value = int(value)
                            config[key] = value
                
                buffer.append({"type": "battle", "config": config, "branches": branches})
                continue
            
            # Add maze command parsing
            # Di dalam parse_story function, bagian parsing \maze:
            if line.startswith("\\maze"):
                # Format: \maze map_name="forest" description="Escape!" win=success_scene lose=fail_scene F1=scene_a F2=scene_b
                config = {}
                branches = {}
                parts = line.split()
                
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        
                        # Handle ALL branch targets - bukan cuma win/lose
                        # Bisa berupa: win, lose, F, F1, F2, F3, default, dll
                        if key in ['win', 'lose', 'draw', 'surrender', 'default']:
                            branches[key] = value
                        elif key.startswith('F'):  # Tangkap F, F1, F2, F3, dst
                            # Cek jika key adalah finish point (F atau F diikuti angka)
                            if key == 'F' or (key.startswith('F') and key[1:].isdigit()):
                                branches[key] = value
                        else:
                            # Handle config values
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.isdigit():
                                value = int(value)
                            config[key] = value
                
                buffer.append({"type": "maze", "config": config, "branches": branches})
                continue
            
            if line.startswith("\\hangman"):
                branches = {}
                config = {"words": []}
                
                # Cari apakah ada words(...)
                if "words(" in line:
                    # Ekstrak words dari dalam parentheses
                    start_idx = line.find("words(") + 6  # setelah "words("
                    end_idx = line.find(")", start_idx)
                    if end_idx != -1:
                        words_str = line[start_idx:end_idx]
                        # Parse kata-kata yang dipisahkan koma
                        words = []
                        current_word = ""
                        in_quotes = False
                        
                        for char in words_str:
                            if char == '"' or char == "'":
                                in_quotes = not in_quotes
                            elif char == ',' and not in_quotes:
                                if current_word.strip():
                                    words.append(current_word.strip())
                                    current_word = ""
                            else:
                                current_word += char
                        
                        # Add last word
                        if current_word.strip():
                            words.append(current_word.strip())
                        
                        # Clean quotes from words
                        clean_words = []
                        for word in words:
                            # Remove surrounding quotes if present
                            if (word.startswith('"') and word.endswith('"')) or \
                            (word.startswith("'") and word.endswith("'")):
                                word = word[1:-1]
                            clean_words.append(word)
                        
                        config["words"] = clean_words
                        
                        # Remove words(...) bagian dari line untuk parsing selanjutnya
                        line = line.replace(f"words({words_str})", "").strip()
                
                # Parse sisanya untuk branches
                parts = line.split()
                
                # Lewati "\hangman"
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        if key in ['win', 'lose']:
                            branches[key] = value
                        elif key == 'category':
                            config['category'] = value
                
                buffer.append({"type": "hangman", "config": config, "branches": branches})
                continue
            
    if current_scene is not None:
        scenes[current_scene] = buffer
    
    return scenes


# ==============================
# VALIDATOR FUNCTIONS
# ==============================

def validate_engine():
    """Validator untuk parser.py"""
    import sys
    import os
    import tempfile
    
    try:
        # SUPPRESS ALL OUTPUT
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        with open(os.devnull, 'w') as fnull, \
             redirect_stdout(fnull), \
             redirect_stderr(fnull):
            
            # 1. CREATE TEST STORY FILE
            test_story = """\\scene start
$cyan === PARSER TEST ===
This is a parser test.

\\choice "Go to scene2" goto scene2
\\choice "Go to end" goto end

\\scene scene2
\\bold This is bold text
\\divider *
\\pause "Press Enter..."
\\progress 1 "Processing"
\\goto end

\\scene end
$green ✅ PARSER TEST COMPLETE
"""
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.story', delete=False, encoding='utf-8') as f:
                f.write(test_story)
                temp_path = f.name
            
            try:
                # 2. TEST parse_story FUNCTION
                import engine.parser as parser_module
                
                scenes = parser_module.parse_story(temp_path)
                
                # 3. VALIDATE PARSED STRUCTURE
                required_scenes = ["start", "scene2", "end"]
                scene_check = all(scene in scenes for scene in required_scenes)
                
                # Check scene content
                content_check = True
                errors = []
                
                if "start" in scenes:
                    start_cmds = scenes["start"]
                    # Should have color text and 2 choices
                    color_cmd = [c for c in start_cmds if c.get("type") == "color"]
                    choice_cmds = [c for c in start_cmds if c.get("type") == "choice"]
                    
                    if len(color_cmd) != 1:
                        content_check = False
                        errors.append("Missing color command in start scene")
                    if len(choice_cmds) != 2:
                        content_check = False
                        errors.append(f"Expected 2 choices in start, got {len(choice_cmds)}")
                
                if "scene2" in scenes:
                    scene2_cmds = scenes["scene2"]
                    cmd_types = [c.get("type") for c in scene2_cmds]
                    expected_types = ["bold", "divider", "pause", "progress", "goto"]
                    
                    for expected in expected_types:
                        if expected not in cmd_types:
                            content_check = False
                            errors.append(f"Missing {expected} command in scene2")
                
                # 4. TEST WITH SPECIAL COMMANDS
                special_story = """\\scene test
\\battle player_hp=50 enemy_hp=50 win=win_scene lose=lose_scene
\\maze map_name="test" description="Test" win=win_maze lose=lose_maze F1=finish1
\\hangman category="horror" win=win_hangman lose=lose_hangman
"""
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.story', delete=False, encoding='utf-8') as f:
                    f.write(special_story)
                    special_path = f.name
                
                try:
                    special_scenes = parser_module.parse_story(special_path)
                    
                    if "test" in special_scenes:
                        test_cmds = special_scenes["test"]
                        special_cmd_types = [c.get("type") for c in test_cmds]
                        
                        # Check for battle, maze, hangman commands
                        if "battle" not in special_cmd_types:
                            content_check = False
                            errors.append("Battle command not parsed")
                        if "maze" not in special_cmd_types:
                            content_check = False
                            errors.append("Maze command not parsed")
                        if "hangman" not in special_cmd_types:
                            content_check = False
                            errors.append("Hangman command not parsed")
                finally:
                    if os.path.exists(special_path):
                        os.unlink(special_path)
                
                # 5. FINAL VALIDATION
                ok = scene_check and content_check
                
                result_info = {
                    "scenes_found": len(scenes),
                    "scene_names": list(scenes.keys())
                }
                
                if not ok and errors:
                    result_info["errors"] = errors
                
                return {
                    "module": "parser",
                    "ok": ok,
                    "result": result_info
                }
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    except Exception as e:
        return {
            "module": "parser",
            "ok": False,
            "error": f"{type(e).__name__}: {str(e)[:100]}"
        }
