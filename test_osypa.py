import re

TIME_REGEX = re.compile(r'(\d{1,2}[:.]\d{2})([\*]*)')

txt = "06:05, 06:35, 07:05, 07:35, 08:05 - 09:05 (every 15 minutes), 09:25 - 11:00 (every 20 minutes),11:20, 11:35, 11:45, 11:55, 12:10, 12:20, 12:35, 12:50, 13:10, 13:25, 13:45, 14:00, 14:10, 14:20, 14:35, 14:55, 15:10, 15:30, 15:45, 16:05, 16:20, 16:55, 17:30, 18:05, 18:40, 19:20 – 23:20 (every 30 minutes)"

print(f"Text length: {len(txt)}")

if len(txt) > 200:
    print("REJECTED by original code (len > 200)")

if len(txt) > 800:
    print("REJECTED by new code (len > 800)")
else:
    raw_times = TIME_REGEX.findall(txt)
    print(f"Found {len(raw_times)} times: {raw_times[:5]}...")
