# Notes on this todo list CLI

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


### before this was done:

These are all copy pasted thinking work i did while creating this todo list maker.

(never did this):
note: cd c:/Users/grayd/OneDrive/Desktop/private_notes/scratch    
until I make a .venv / nuke the one i'm in


# plan:


### Commands are: `add`, `list`, `done`, `delete`, `edit`, `clear`.


### Add: 
   task.json is generated.
   with fields `id`, `text`, `created_at`, `done`
   Optionally: `due_date`, `priority`, `tags`
   saves file.
   on failure to add give clear error


### list
filtering: `show all` / `only not done` / `only done`.


### Done
load json
ensure exists 
could ensure not already marked done
tmp save change
replace


### delete
Decide if confirmation or not.
'all', or just one? (or input which ones by name only)
could specify using fields.
on failure to delete give clear error


## edit
change any/some fields. (text, due_date, priority, tags)    # ill ingore 'done' editing, thats it's own task
this must simultaniously add (while paying attention to what was there before)
and then delete the other file
on failure to do either, wipe both, give clear error


## clear
How is clear different to delete?
does it stop them being 'open'?
Ill make it a reset to defaults (only editables)





