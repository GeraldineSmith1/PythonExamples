from datetime import datetime

####################################################################################################################
# Purpose: To identify how well the different English regions are responding to lockdown.
# Assumption is that the peak occurs on April 8th (2 weeks after lockdown began)
# Some areas are responding better than others. This reports a progress factor for each region which is computed by
# taking the average daily case count since the "peak" and dividing that into the daily case count on April 8th
# Logic is a little flawed but provides a useful indicator for identification of what is happening below England level
####################################################################################################################

debug = False
input_file_name = "C:\\Geraldine\\Coronavirus\\coronavirus-cases20200427.csv"
output_file_name = "C:\\Geraldine\\Coronavirus\\coronavirus-output_results.csv"
start_date_string = "2020-03-01"
peak_date_string = "2020-04-08"

date_object = datetime.strptime(start_date_string, "%Y-%m-%d")
peak_date_object = datetime.strptime(peak_date_string, "%Y-%m-%d")


def read_stats_file(csv_file_name):
    """ Reads the daily gov.uk covid 19 csv file and returns a dictionary where:
            key fields are the countries/regions
            values are a list of dates and daily case counts  """
    the_dictionary = {}
    linecount = 0
    fileobject = open(csv_file_name)
    for line in fileobject:
        linecount += 1
        # TODO Add a check for a double quote in position 1
        field_list = line.split(",")
        new_line_value_list = [(field_list[3], field_list[4])]
        # if field_list[0] != "England" and field_list[0] != "Wiltshire":
        #     continue
        if debug:
            print("Region is ==> {}".format(field_list[0]))
        existing_value_list = the_dictionary.get(field_list[0])
        if existing_value_list is None:
            the_dictionary[field_list[0]] = new_line_value_list
        else:
            existing_value_list.append(new_line_value_list)
            the_dictionary[field_list[0]] = existing_value_list
    if debug:
        print("\n\n Input File has been processed. Line count is {}".format(linecount))
        print("Dict for region ==>  {} {} ".format("England", the_dictionary.get("England")))
    fileobject.close()
    return the_dictionary


country_dictionary = None
try:
    country_dictionary = read_stats_file(input_file_name)
except Exception as exc:
    print("Error reading daily stats file {}".format(input_file_name))
    print("\t\t{}".format(exc))
    exit(-1)

# TODO: The following logic needs to be improved
############################################################################################################
# Now process each region: Compute the average daily case count since the peak date and compare with the
# value on the peak date
# Write results a csv output file plus stdout
############################################################################################################
results_file = None
try:
    results_file = open(output_file_name, "w")
except Exception as exc:
    print("Error opening output file {}".format(input_file_name))
    print("\t\t{}".format(exc))
    exit(-2)

output_header = "Region,Peak Case Count, Recent Average, Progress Factor\n"
results_file.write(output_header)
region_count = 0
for region in country_dictionary:
    region_count += 1
    # TODO
    # Some region names are prefixed with a double quote and contain commas which breaks the parsing logic
    # This needs to be fixed
    if region.startswith('"'):
        continue
    region_values = country_dictionary.get(region)
    i = 0
    peak_case_count = 0
    recent_count = 0
    recent_total = 0
    recent_average = 0
    for dategroup in region_values:
        i += 1
        # print("{} ==> {}".format(i, type(dategroup)))
        if i == 1:
            continue
        if debug:
            print("date is {} = type is {}".format(dategroup[0][0], type(dategroup[0][0])))
        date_object = datetime.strptime(dategroup[0][0], "%Y-%m-%d")
        if dategroup[0][1] == "":
            casecount = 0
        else:
            casecount = int(dategroup[0][1])

        if date_object > peak_date_object:
            # WE ARE INTERESTED (results should be improving )
            recent_total = recent_total + casecount
            recent_count += 1
        elif date_object == peak_date_object:
            # We are interested - this should be the peak case count
            peak_case_count = casecount
        else:
            # We are not interested - these dates are before the peak / lockdown start
            pass

    if recent_count > 0:
        recent_average = recent_total / recent_count
    if recent_average < 1:
        recent_average = 1

    # TODO replace this logic - compute the weekly average for the peak week instead of using a single day
    # TODO instead of overall average since peak date, use rolling 7 day average
    progress_factor = peak_case_count / recent_average

    print("{:<3}: Region ==> {:<30} peak count ==> {:<5} recent average is ==> {:7.1f}  progress_factor is ==> {:3.2f}"
          .format(region_count, region, peak_case_count, recent_average, progress_factor))
    output_line = "{:<30},{:<5},{:7.1f},{:3.2f}\n".format(region, peak_case_count, recent_average, progress_factor)
    results_file.write(output_line)

    if recent_average > peak_case_count:
        pass
        # print(" {}: HIGH ALARM For Region ==> {} peak count is ==> {} recent average is ==>{:10.2f}"
        # .format(region_count, region, peak_case_count, recent_average))
results_file.close()
print("\nOutput Results have been written to {} ".format(output_file_name))

# TODO: For England and poorly performing regions produce graphical output
