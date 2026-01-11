"""
## CLI todo list app.


Options:

Commands are: `add`, `list`, `done`, `delete`, `edit`, `clear`.

Each task has `id`, `input_text`, `created_at`, `done` (boolean). 
Optionally: `due_date`, `urgency`, `tags` (can be changed on `add` and `edit`)

Persistent storage: JSON does not corrupt if interrupted. 

"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import io
import datetime
from pathlib import Path


# keep main clean
def normalize_fields(args):
    """Stores user inputs into a single dict that can be passed around."""

    # fetch
    input_text = getattr(args, "input_text")            
    due_date = getattr(args, "due_date")
    urgency = getattr(args, "urgency")
    tags = getattr(args, "tags")
    saved_to = getattr(args, "saved_to")    # should have checked this here
    show = getattr(args, "show")   
    name = getattr(args, "name") 

    # force_delete_all logic:
    force_delete_all = getattr(args, "force_delete_all") 
    
    def t_or_f(bool_flag):
        ua = str(bool_flag).upper()
        if 'TRUE'.startswith(ua):
            return True
        elif 'FALSE'.startswith(ua):
            return False
        else: 
            pass

    force_delete_all = t_or_f(force_delete_all)
            

    user_input = {"input_text": input_text, "due_date": due_date, 
                  "urgency": urgency, "tags": tags, 
                  "saved_to": saved_to, "show": show, 
                  "name": name, "force_delete_all": force_delete_all}    
    
    return user_input    

def input_command(command, user_input):
    """Command sorter (should have been a registry)."""
    cmd = command.lower()

    if cmd == "add":
        res = add_task(user_input)
        return res
    
    elif cmd == "list":
        res = list_task(user_input)
        return res   

    elif cmd == "done":
        res = mark_task_done(user_input)
        return res        

    elif cmd == "delete":
        res = delete_task(user_input)
        return res
    
    elif cmd == "edit":
        res = edit_task(user_input)
        return res  
    
    elif cmd == "clear":
        res = clear_task(user_input)
        return res 
    
    else:
        print("Invalid command, please try one of: --add / --list / --done / --delete / --edit / --clear, "
        "(and ensure no spaces, caps, etc)")
        return 1

# exposed helpers
def save_json(todo_schema, saved_to, name=None):
    """Saves json into a tmpdir, then renames to intended location once written (prevents corruption)."""

    if name == None:
        num = 1 + len([name for name in os.listdir(saved_to) if os.path.isfile(os.path.join(saved_to, name))])  # prevents collisions on add
        name = f"task_{num}.json"
    else:
        name = name


    tmp_dir = tempfile.mkdtemp(dir=saved_to)    # saves to working directory
    Path(tmp_dir)


    tmp_file = "tmp.json"
    tmp_path = tmp_dir / Path(tmp_file)


    try:
        with open(tmp_path, "w") as outfile:
            json.dump(todo_schema, outfile)
            io.IOBase.flush(outfile)
            os.fsync(outfile)
            # file is now saved

        if os.path.exists(saved_to / name):
            # my deleting efforts failed so this:
            trash_dir = "trash/"
            trash_dir = Path(trash_dir)

            os.makedirs(trash_dir, exist_ok=True)
            num = 1 + len([name for name in os.listdir(trash_dir) if os.path.isfile(os.path.join(trash_dir, name))])    # prevents collisions in the trash

            os.renames(saved_to/name, trash_dir/f"deleted_{num}.json")

        os.renames(tmp_path, saved_to / name)


    except Exception:
        print("Save failed or crashed. Please try again.")
        raise RuntimeError()
    
    print(f"Saved {name} to: {saved_to}")
        
    return None

def load_json(dir_path):
    """Loads json file."""
    # ensure exists check?
    with open(dir_path) as f:
        data = json.load(f)
        return data
    
# commands
def add_task(user_input):
    """Adds a new task. Without a user provided name, save_json's logic will generate one."""

    input_text = user_input["input_text"]
    if input_text == None:
        print("input_text is required for adding new a task.")
        return 1
        

    # optionals:
    due_date = user_input["due_date"]             # these are user input only
    urgency = user_input["urgency"]    
    tags = user_input["tags"]    


    # path
    saved_to = user_input["saved_to"]
    os.makedirs(saved_to, exist_ok=True)
    saved_to = Path(saved_to)

    name = user_input["name"]


    # defaults (cannot be modified after add):
    def _make_id(saved_to):
        return 1 + len([name for name in os.listdir(saved_to) if os.path.isfile(os.path.join(saved_to, name))])    

    id = _make_id(saved_to)
    created_at = str(datetime.date.today())    
    done = False            # default false on add

    todo_schema = {"id": id, 
                   "input_text": input_text, 
                   "created_at": created_at, 
                   "done": done,
                   "due_date": due_date,
                   "urgency": urgency,
                   "tags": tags}

    # saving
    save_json(todo_schema, saved_to, name=name)
    print(f"Added {name} sucessfully in {saved_to}.")
    return 0

def list_task(user_input):
    """Loading one specifed task: prints that task's output. `--show`: takes a dir, only loads filenames"""

    show = user_input["show"]     
    saved_to = user_input["saved_to"]

    if saved_to == None:
        print("Please enter a path using --saved_to to list files.")
        return 1

    try: 
        check = os.path.isdir(saved_to) 
    except Exception:
        check = False


    if show != None and check == False:
        print("Error: to use --show, please enter a directory, not a filepath.")
        return 1

    elif show == None and check == True:
        print("Error: please enter a filepath to show its task (use --show to list directory contents).")
        return 1

    if not os.path.exists(saved_to):
        print(f"Cannot find {saved_to} from input. Please double check your file path to --saved_to.")
        return 1        

    saved_to = Path(saved_to)

    # we have files 
    # under /todo_lists/<files>
    if show == None:
        data = load_json(saved_to)

        # unpack data
        id = data["id"]
        input_text = data["input_text"]
        created_at = data["created_at"]
        done = data["done"]
        due_date = data["due_date"]
        urgency = data["urgency"]
        tags = data["tags"]

        # CLI prints
        print(f"\nTHIS TODO LIST IS FROM: {saved_to}\n")

        print(f' text says: "{input_text}"')
        print("     Is-Done-Status:", done)
        print("     Created on:", created_at)
        print("     ID:", id)

        print("  Extras:")
        print("     Due date:", due_date)
        print("     Urgency:", urgency)
        print("     Tags:", tags)

        print(f"\n(Full todo list contents are: {data})\n")
        return 0
    
    # or: show all in directory.

    elif show == "all":

        if os.listdir(saved_to) == []:
            print("No tasks to show.")
            return 0
   
        print(f"Your files and tasks under {saved_to} are:")
        for name in os.listdir(saved_to):
            if os.path.isfile(os.path.join(saved_to, name)):
                print(f"- {name}")
        print(f"\nInput a file path to `--saved_to` (ex: {saved_to}/<task>) "
                "with no `--show` command to view a single task in more detail.\n")
        return 0

    # or: done filtering
    elif show == "not_done" or "done": 

        if show == "not_done": cond = False 
        elif show == "done": cond = True

        print(f"Showing tasks with status: `{show}` :") 

        if os.listdir(saved_to) == []:
            print("No tasks to show.")
            return 0

        count = 0
        for name in os.listdir(saved_to):

            if os.path.isfile(os.path.join(saved_to, name)) and os.path.basename(".json"):
                loaded = load_json(saved_to / name)
                done = loaded["done"]
                if done == cond:
                    print(f"- {name}")
                    count += 1

        if count == 0:
            print("No tasks to show.")
            return 0
            
        print(f"\nInput a file path to `--saved_to` (ex: {saved_to}/<task>) "
        "with no `--show` command to view a single task in more detail.\n")
        return 0
    
    else: 
        print("Invalid show command. For `--show`, please try one of: all / done / not_done")
        return 1

def mark_task_done(user_input):
    """Marks a task done: if done is False, change to True."""
    saved_to = user_input["saved_to"] 
    dir, name = os.path.split(saved_to)
    dir = Path(dir)

    if os.path.isfile(saved_to) and os.path.basename(".json"):
        loaded = load_json(saved_to)
        done = loaded["done"]
        if done == False:
            loaded["done"] = True
            save_json(loaded, dir, name)
            print(f"Marked {name} Done.")
        else: 
            print("This Task is already marked Done.")
        return 0

    else: 
        print(F"No file found at {saved_to}. Please check your input path "
              "(and ensure you're not inputing a directory).")
        return 1
    
def delete_task(user_input):
    """Deletes a task (uses renaming method, not disk deletion). Use `--force_delete_all` to delete an entire directory of tasks."""
    saved_to = user_input["saved_to"]
    saved_to = Path(saved_to)

    force_delete_all = user_input["force_delete_all"]

    is_dir = os.path.isdir(saved_to)

    # check exists before deleting
    if os.path.exists(saved_to):
        trash_dir = "trash/"
        trash_dir = Path(trash_dir)

        os.makedirs(trash_dir, exist_ok=True)


        if force_delete_all == True:    

            # make sure this is a directory
            if is_dir == False:
                print("Input a dir to delete all tasks (not a path to a file)")
                return 1

            if os.listdir(saved_to) == []:
                print(f"No files to delete in {saved_to}")

            for name in os.listdir(saved_to):
                if os.path.isfile(os.path.join(saved_to, name)):
                    num = 1 + len([name for name in os.listdir(trash_dir) if os.path.isfile(os.path.join(trash_dir, name))])    # ensure no collisons
                    os.renames(saved_to / name, trash_dir/f"deleted_{num}.json")

            print(f"All files in {saved_to} deleted.")
            return 0

        else:
            # make sure this is not a directory
            if is_dir == True:
                print("Input a path to a task to be deleted (not a dir. Use --force_delete_all to delete a dir).")
                return 1
            
            num = 1 + len([name for name in os.listdir(trash_dir) if os.path.isfile(os.path.join(trash_dir, name))])    # ensure no collisons
            os.renames(saved_to, trash_dir/f"deleted_{num}.json")

            print(f"File {saved_to} deleted.")
            return 0

    else: 
        print(F"File(s) already deleted (or incorrect path provided/does not exist: {saved_to})")
        return 0

def edit_task(user_input):
    """Edit user editable text fields. Does not replace fields on None."""
    saved_to = user_input["saved_to"]

    dir, name = os.path.split(saved_to)
    dir = Path(dir)

    editable = os.path.isfile(saved_to)

    if not editable:
        print(f"Error: File not found at `{saved_to}`. Please ensure your path is to a file.")
        return 1

    # editable fields
    new_input_text = user_input["input_text"]
    new_due_date = user_input["due_date"]
    new_urgency = user_input["urgency"]
    new_tags = user_input["tags"]

    loaded = load_json(saved_to)

    def assign_new_value(loaded, key, new_value):
        if new_value != None:
            loaded[key] = new_value
        return None

    # update loaded:
    assign_new_value(loaded, "input_text", new_input_text)
    assign_new_value(loaded, "due_date", new_due_date)
    assign_new_value(loaded, "urgency", new_urgency)
    assign_new_value(loaded, "tags", new_tags)

    # save
    save_json(loaded, dir, name)

    print(f"Edited {saved_to} successfully.")

def clear_task(user_input):
    """Clear editable fields text fields (replace with `None`)."""
    saved_to = user_input["saved_to"]

    dir, name = os.path.split(saved_to)
    dir = Path(dir)

    clearable = os.path.isfile(saved_to)

    if not clearable:
        print(f"Error: File not found at `{saved_to}`. Please ensure your path is to a file.")
        return 1

    # load file
    loaded = load_json(saved_to)

    # set all editable fields to `None`
    loaded["input_text"] = None
    loaded["due_date"] = None
    loaded["urgency"] = None
    loaded["new_tags"] = None

    # save
    save_json(loaded, dir, name)

    print(f"Cleared {saved_to}'s editable content successfully.")    
    return 0

# main
def main():
    """
    Entrypoint CLI for task maker.

    # usage examples:

    ## add:
    python -m CLI_todo_app --command add --input_text "New Todo List." --due_date "tommorow" --urgency "urgent" --tags "admin" "sunny" --name "newtask.json"

    ## list: 
    python -m CLI_todo_app --command list --show all

    ## done:
    python -m CLI_todo_app --command done --saved_to todo_lists/newtask.json

    ## edit
    python -m CLI_todo_app --command edit --saved_to todo_lists/newtask.json --input_text "New text for this file" --due_date "Two weeks" --urgency "Less urgent now"

    ## clear
    python -m CLI_todo_app --command clear --saved_to todo_lists/newtask.json 

    ## delete
    python -m CLI_todo_app --command delete --saved_to todo_lists/newtask.json

    """

    parser = argparse.ArgumentParser(description="Todo list with basic functionality.", add_help=True)


    # all commands
    parser.add_argument("--command", help="Usable commands are: add / list / done / delete / edit / clear")

    # user editable:
    parser.add_argument("--input_text", help="(add, edit): Input text for your todo list.")
    parser.add_argument("--due_date", help="(add, edit): Add / modify the due-date for this task.")
    parser.add_argument("--urgency", help="(add, edit): Add / modify the urgency for this task.")
    parser.add_argument("--tags", nargs='+', help="(add, edit): Add / modify tags for this task. (no spaces): a b c) -> [a, b, c]")

    # add
    parser.add_argument("--name", help="(add): name your file upon creation.")

    # list
    parser.add_argument("--show", help="(list): fiter via one of four methods: all / done / not_done / none")
    
    # delete
    parser.add_argument("--force_delete_all", help="(delete): delete all files in a given directory. (True / False)", default=False)


    # out dir
    parser.add_argument("--saved_to", help="Fetches and/or saves the list from a directory.", default="todo_lists/")



    # this parses args into a Namespace
    args = parser.parse_args()


    user_input = normalize_fields(args)


    # command sorter
    if args.command:
        res = input_command(args.command, user_input)
        if res == 1:
            raise RuntimeError("Error from given command.")

        # close
    else: 
        raise KeyError("Please use a command.")


if __name__ == "__main__":
    main() 