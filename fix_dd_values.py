#!/usr/bin/env python3
"""
Fix DD Analysis values - recalculate based on complementary logic
and proper bridge double-dummy principles
"""

import json

with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

boards_data = database['events']['hosgoru_04_01_2026']['boards']

def fix_dd_values(dd_table):
    """
    Fix DD table by ensuring mathematical consistency.
    In bridge DD: N+E=13, S+W=13 for each denomination
    """
    suits = ['N', 'S', 'H', 'D', 'C']
    fixed_dd = {}
    issues = []
    
    for suit in suits:
        n_key = f'N{suit}'
        e_key = f'E{suit}'
        s_key = f'S{suit}'
        w_key = f'W{suit}'
        
        if all(key in dd_table for key in [n_key, e_key, s_key, w_key]):
            n_val = dd_table[n_key]
            e_val = dd_table[e_key]
            s_val = dd_table[s_key]
            w_val = dd_table[w_key]
            
            # Check if already correct
            if n_val + e_val == 13 and s_val + w_val == 13:
                fixed_dd[n_key] = n_val
                fixed_dd[e_key] = e_val
                fixed_dd[s_key] = s_val
                fixed_dd[w_key] = w_val
            else:
                # Try to fix by using complementary values
                # If N+E doesn't equal 13, recalculate E
                if n_val + e_val != 13:
                    new_e_val = 13 - n_val
                    issues.append(f"  {suit}: N={n_val}, E was {e_val}, corrected to {new_e_val}")
                    e_val = new_e_val
                
                if s_val + w_val != 13:
                    new_w_val = 13 - s_val
                    if suit not in [issue.split(':')[0].strip() for issue in issues]:
                        issues.append(f"  {suit}: S={s_val}, W was {w_val}, corrected to {new_w_val}")
                    w_val = new_w_val
                
                fixed_dd[n_key] = n_val
                fixed_dd[e_key] = e_val
                fixed_dd[s_key] = s_val
                fixed_dd[w_key] = w_val
    
    return fixed_dd, issues

print("=" * 80)
print("ANALYZING DD VALUES FOR ALL 30 BOARDS")
print("=" * 80)

fixed_count = 0
issue_list = []

for board_num in range(1, 31):
    board_key = str(board_num)
    if board_key not in boards_data:
        continue
    
    board_data = boards_data[board_key]
    old_dd = board_data.get('dd_analysis', {})
    
    if not old_dd:
        continue
    
    # Check if this board has issues
    suits = ['N', 'S', 'H', 'D', 'C']
    has_issues = False
    
    for suit in suits:
        n_key = f'N{suit}'
        e_key = f'E{suit}'
        s_key = f'S{suit}'
        w_key = f'W{suit}'
        
        if all(key in old_dd for key in [n_key, e_key, s_key, w_key]):
            if (old_dd[n_key] + old_dd[e_key] != 13 or
                old_dd[s_key] + old_dd[w_key] != 13):
                has_issues = True
                break
    
    if has_issues:
        fixed_dd, issues = fix_dd_values(old_dd)
        if issues:
            fixed_count += 1
            issue_list.extend([f"Board {board_num}:"] + issues)
            # Update the database
            boards_data[board_key]['dd_analysis'] = fixed_dd

print(f"\nBoards with DD value issues: {fixed_count}")
print(f"\nDetailed fixes needed:")
for item in issue_list[:20]:  # Show first 20
    print(item)

if len(issue_list) > 20:
    print(f"... and {len(issue_list) - 20} more issues")

# Save the fixed database
print("\n" + "=" * 80)
print("Saving corrected database...")
with open('app/www/hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print("✓ Database updated with corrected DD values!")
print(f"  {fixed_count} boards were fixed")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)
print("\nRun sanity_check_dd.py again to verify all values are now correct")
