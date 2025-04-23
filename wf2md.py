#%%
from pathlib import Path
import pandas as pd
import hashlib

root_dir = Path(__file__).parent
import_dir = root_dir / 'import'
try:
    import_path = list(import_dir.glob('*.txt'))[0]
except IndexError:
    raise FileNotFoundError(f'No txt file found in {import_dir}. You need to export your Workflowy notes to txt first. See the README for instructions.')
export_dir = root_dir / 'export'

# Create export directory if it doesn't exist
export_dir.mkdir(exist_ok=True)

FORBIDDEN_FN_CHARS =  [':', '/']
# These characters are supposedly forbidden on Windows: ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

def get_safe_filename(title, max_length=100):
    """Convert a title to a safe filename, handling long titles by truncating and adding a hash."""
    # Remove forbidden characters
    for char in FORBIDDEN_FN_CHARS:
        title = title.replace(char, '-')
    
    # If title is short enough, return as is
    if len(title) <= max_length:
        return title
    
    # Generate a hash of the full title
    title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
    
    # Truncate the title but keep the beginning and end
    half_length = (max_length - len(title_hash) - 3) // 2
    truncated = f"{title[:half_length]}...{title[-half_length:]}"
    
    # Combine with hash
    return f"{truncated}-{title_hash}"

#%% Conversing nested list in txt to nested json

with open(import_path, 'r') as f:
    lines = f.readlines()

note_dfs = []
note_rows = []  # Initialize note_rows before the loop

for i, line in enumerate(lines):
    # Get hierarchy level by counting how many double-spaces the line starts with
    level = int((len(line) - len(line.lstrip(' '))) / 2)
    
    text = line.strip()[2:]
    
    if level == 0:
        # Format string as Obsidian tag
        tag = text.replace(' ', '-').replace('/', '-').lower()
        continue
    if level == 1:
        if i > 1:
            # Here, data for a complete note has been collected and we can create a dataframe for it.
            note_df = pd.DataFrame(note_rows, columns=['Tags', 'Title', 'Level', 'Text'])
            note_dfs.append(note_df)
        
        

        # Initializing/resetting the note rows
        note_rows = []

        # If title contains tags, extract them to tags and remove from title
        if '#' in text:
            title, *tags = text.split(' #')
        else:
            tags = []
            title = text
        
        # Make title into a valid filename
        for char in FORBIDDEN_FN_CHARS:
            title = title.replace(char, '-')

        tags = ['workflowy-import', tag] + tags
        tags = [tag.strip() for tag in tags]
        
        continue
    
    h1 = text
    note_rows.append([tags, title, level-1, text])


#%% 

# This decides which format should be used for each level of note, based on the max level of the note. The first item in the tuple is the prefix, and the second item is the suffix. I try to follow https://www.markdownguide.org/basic-syntax/ as much as possible.

# Track unmapped levels
unmapped_levels = set()

def get_format_for_level(max_level, current_level):
    if current_level > max_level:
        unmapped_levels.add(current_level)
        return ['', '']  # Default to plain text for unmapped levels
    
    if max_level not in LEVEL_TO_FORMAT_MAP:
        unmapped_levels.add(max_level)
        return ['', '']  # Default to plain text for unmapped max levels
        
    if current_level not in LEVEL_TO_FORMAT_MAP[max_level]:
        unmapped_levels.add(current_level)
        return ['', '']  # Default to plain text for unmapped levels
        
    return LEVEL_TO_FORMAT_MAP[max_level][current_level]

LEVEL_TO_FORMAT_MAP = {
    # In notes with only one level, that level should be plain text
    1: {
        1: ['', ''],
    },
    # In notes with two levels, the first level should be a header and the second level should be plain text
    2: {
        1: ['\n# ', '\n'],
        2: ['', ''],
    },
    # In notes with three levels, the first level should be a header, the second level should be a subheader, and the third level should be plain text
    3: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['', ''],
    },
    # In notes with four levels, level 1-3 should be as above, and level 4 should be bullet points
    4: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['', ''],
        4: ['* ', ''],
    },
    # In notes with five levels, level 1-4 should be as above, and level 5 should be level 2 bullet points
    5: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['', ''],
        4: ['* ', ''],
        5: ['\t* ', ''],
    },
    # In notes with six levels, level 1-3 should be headers, level 4 text and level 5-6 bullet points
    6: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['\n### ', '\n'],
        4: ['', ''],
        5: ['* ', ''],
        6: ['\t* ', ''],
    },
    # In notes with seven levels, level 1-3 should be headers, level 4 text and level 5-7 bullet points
    7: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['\n### ', '\n'],
        4: ['', ''],
        5: ['* ', ''],
        6: ['\t* ', ''],
        7: ['\t\t* ', ''],
    },
    # In notes with eight levels, level 1-3 should be headers, level 4 text and level 5-8 bullet points
    8: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['\n### ', '\n'],
        4: ['', ''],
        5: ['* ', ''],
        6: ['\t* ', ''],
        7: ['\t\t* ', ''],
        8: ['\t\t\t* ', ''],
    },
    # In notes with nine levels, level 1-3 should be headers, level 4 text and level 5-9 bullet points
    9: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['\n### ', '\n'],
        4: ['', ''],
        5: ['* ', ''],
        6: ['\t* ', ''],
        7: ['\t\t* ', ''],
        8: ['\t\t\t* ', ''],
        9: ['\t\t\t\t* ', ''],
    },
    # In notes with ten levels, level 1-3 should be headers, level 4 text and level 5-10 bullet points
    10: {
        1: ['\n# ', '\n'],
        2: ['\n## ', '\n'],
        3: ['\n### ', '\n'],
        4: ['', ''],
        5: ['* ', ''],
        6: ['\t* ', ''],
        7: ['\t\t* ', ''],
        8: ['\t\t\t* ', ''],
        9: ['\t\t\t\t* ', ''],
        10: ['\t\t\t\t\t* ', ''],
    }
}


df = (
    pd.concat(note_dfs, ignore_index=True)
    
    # Drop empty rows
    .loc[lambda x: x.Text.str.len() > 0]

    # Assign max level of each Title
    .assign(MaxLevel=lambda x: x.groupby('Title').Level.transform('max'))
    
    # TODO: Figure out workflowy "mirrors" by identically named rows in different places in the tree and apply Obsidian's linkage between them instead.
    
    # Assign the prefix and suffix for each row
    .assign(Prefix=lambda x: x.apply(lambda row: get_format_for_level(row.MaxLevel, row.Level)[0], axis=1))
    .assign(Suffix=lambda x: x.apply(lambda row: get_format_for_level(row.MaxLevel, row.Level)[1], axis=1))

    # Finalize the output text
    .assign(Output=lambda x: x.Prefix + x.Text + x.Suffix)

    # Replace "/" with "-" in titles because filenames cannot contain "/"
    .assign(Title=lambda x: x.Title.str.replace('/', '-'))
)
   
#%% Export to markdown files

for title, note_df in df.groupby('Title'):
    safe_title = get_safe_filename(title)
    with open(export_dir / f'{safe_title}.md', 'w') as f:
        # Write the tags starting with a # and separated by spaces
        f.write('#' + ' #'.join(note_df.Tags.iloc[0]) + '\n')

        # Write the note
        f.write(note_df.Output.str.cat(sep='\n'))

print(f'Exported {len(df.Title.unique())} notes to {export_dir}')

# Print unmapped levels at the end
if unmapped_levels:
    print(f"Warning: The following levels were not mapped and defaulted to plain text: {sorted(unmapped_levels)}")

#%%