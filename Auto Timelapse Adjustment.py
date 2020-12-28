import rpa as r

r.init(visual_automation = True, chrome_browser = False)
r.debug(False)


# modify these settings to suit your screen and needs

photo_metadata_location = (656, 2051, 924, 2076)
photo_exposure_box_location = (517, 805)

adjustment_symmetry_start_end = (2, 3) # 0-based index


import math
class ExposureSetting:
  def __init__(self, iso, shutter_speed, aperture, exposure_compensation):
    self.iso = iso
    self.shutter_speed = shutter_speed
    self.aperture = aperture
    self.exposure_compensation = exposure_compensation
    
  def __sub__(self, other):
    iso_stop_diff = round(math.log(self.iso / other.iso, 2) * 3, 0) / 3 # remove *3 and /3 if you have ISO speed that is not aligned to 1/3 stops
    shutter_speed_stop_diff = round(math.log(self.shutter_speed / other.shutter_speed, 2), 2)
    aperture_stop_diff = round(math.log(other.aperture / self.aperture, 2) * 2, 0)
    exp_comp_stop_diff = self.exposure_compensation - other.exposure_compensation
    return round(iso_stop_diff + shutter_speed_stop_diff + aperture_stop_diff + exp_comp_stop_diff, 2)
  
  def __str__(self):
    return f"ISO {self.iso} {round(self.shutter_speed, 5)}s f/{self.aperture} exp.comp.{self.exposure_compensation}"

def interpret_photo_ocr_string(ocr_string):
  # 640 0.55 f/5(s misrecognized)
  metadata = ocr_string.split(" ")
  
  iso_str = metadata[0]
  shutter_speed_str = metadata[1][:-1] # remove "s"
  aperture_str = metadata[2][2:] # remove "f/"
  
  return interpret_photo_metadata(iso_str, shutter_speed_str, aperture_str, "0.0")


def interpret_photo_metadata(iso_str, shutter_speed_str, aperture_str, exposure_comp_str): 
  ss_div_sign_idx = shutter_speed_str.find("/")
  
  if ss_div_sign_idx != -1:
    shutter_speed = 1 / int(shutter_speed_str[ss_div_sign_idx+1:])
  else:
    shutter_speed = float(shutter_speed_str)
    
  return ExposureSetting(int(iso_str), shutter_speed, float(aperture_str), float(exposure_comp_str))

def interpret_user_input(prompt_start_str):
  iso, ss, aperture, exp_comp = input(f"{prompt_start_str} photo settings in 'iso ss aperture exp.comp.':").split()
  return interpret_photo_metadata(iso, ss, aperture, exp_comp)

# input start and end photo index
start_index = int(input("Start photo index:"))
start_exposure = interpret_user_input("Start")
end_index = input("End photo index:")
end_exposure = interpret_user_input("End")


# interactive adjustment solver
total_num_adjustments = int(end_index) - int(start_index)
total_exp_comp_perc_need = int((end_exposure - start_exposure) * 100)

solved_adjustments = [total_num_adjustments, 0, 0, 0, 0]

def sum_adjustments(adjustments):
  sum_val = 0
  for idx, count in enumerate(adjustments):
    sum_val += (idx + 1) * count
  return sum_val

while True:
  print("Current Solution")
  for idx, count in enumerate(solved_adjustments):
    print(f"{idx + 1}%\t{count}")
  
  try:
    human_idx, value = input("Set index value 'index value': ").split()
    idx = int(human_idx) - 1
    value = int(value)
  except KeyboardInterrupt:
    print("Solver aborted!")
    break
  except:
    print("Invalid input!")
    continue
  
  if value < 0 or idx >= len(solved_adjustments) or idx <= 0:
    print("Invalid input!")
    continue
  
  first_value = solved_adjustments[0] -(value - solved_adjustments[idx])
  if first_value < 0:
    print("Input too large!")
    continue
  
  solved_adjustments[0] = first_value
  solved_adjustments[idx] = value
  
  adjustment_diff = sum_adjustments(solved_adjustments) - total_exp_comp_perc_need
  
  if adjustment_diff == 0:
    if input("Solution accepted. Satisfied?[y/n]").lower() == "y":
      break
    else:
      print("Solution not confirmed. You can continue to make adjustments")
  else:
    print("Solution incomplete. Please continue.")
    
    if adjustment_diff > 0:
      advice = "Reduce the number of images for the larger adjustment steps"
    else:
      advice = "Increase the number of images for the larger adjustment steps"
    
    print(f"Current diff = {adjustment_diff}. {advice}")
  
print(f"You've solved the equations! Solution: {solved_adjustments}")


# In[20]:


adjustment_schedule = [None] * (len(solved_adjustments)
                             + (adjustment_symmetry_start_end[1]
                             - adjustment_symmetry_start_end[0] + 1))

# transform solved adjustments into a schedule

for i in range(len(solved_adjustments)):
  if adjustment_symmetry_start_end[0] <= i <= adjustment_symmetry_start_end[1]:
    half_value = solved_adjustments[i] // 2
    adjustment_schedule[i] = (i + 1, half_value)
    adjustment_schedule[(len(solved_adjustments) - 1) * 2 - i] = (i + 1, solved_adjustments[i] - half_value)
  else:
    adjustment_schedule[i] = (i + 1, solved_adjustments[i])

print("final adjustment schedule:", adjustment_schedule)


print("You have 2 seconds to put Capture One window in focus...")

r.wait(2)

print("Start working!")

accumulated_adjustment = 0

for percent_increment, count in adjustment_schedule:
  for _ in range(count):
    # OCR and interpret photo setting
    x1, y1, x2, y2 = photo_metadata_location
    current_photo_exposure = interpret_photo_ocr_string(r.read(x1, y1, x2, y2))
    
    # make adjustment based on accumulator
    x, y = photo_exposure_box_location
    r.click(x, y)
    
    adjust_exp_percentage = int((start_exposure - current_photo_exposure) * 100) + accumulated_adjustment
    if adjust_exp_percentage >= 0:
      sign = ""
    else:
      sign = "-"
      adjust_exp_percentage = -adjust_exp_percentage
    
    adjustment_string = f"{sign}{adjust_exp_percentage//100}.{adjust_exp_percentage%100:02}"
    
    print(current_photo_exposure, "edit exp comp to", adjustment_string)

    r.keyboard(f'{adjustment_string}[enter]')
    
    # accumulate
    accumulated_adjustment += percent_increment
    
    # next photo
    r.keyboard('[ctrl][right]')



r.close()





