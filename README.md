# EdgeProject

### Dataset ###
* DEBS 2015 is described at https://debs.org/grand-challenges/2015/. The full data set is available via a URL posted on the web page 
* The data holds one year worth of data describing taxi trips in NYC; a sub set of the data (first 5K samples) was used in the simulation
* The data has geo locations (latitudes and longitudes) of taxis’ pick-ups and drop-offs and durations of taxi trips; this data is used to create input for EdgeCloudSim (using pipeline.py which currently allows processing the first 5K data samples that span 26 minutes of taxi trips in the data set). Running cells “A”- “E” in the python script will output a csv file “spatial_seriesEdgeCLoudSimInput_REF2” that is to be fed into the EdgeCloudSim 
* Running cell “F” of the python script pipeline.py will produce a plot of x, y positions for the devices (i.e., taxis) and the edge nodes (the nodes’ locations are set in a configuration file of the EdgeCloudSim).  

### Simulation Tool 
* The open-source edge cloud simulation tool EdgeCloudSim is available at https://github.com/CagataySonmez/EdgeCloudSim 
* The tool was used to simulate workloads from devices in taxis moving according to x, y positions produced from the 5K sample obtained from the DEBS 2015 dataset. A deterministic mobility model was used in the tool where the x, y positions of the devices are read in from the “spatial_seriesEdgeCLoudSimInput_REF2” 
* Nine edge nodes were configured, simulation parameters (bandwidths, delays, simulation time, others) were set as well as application parameters were set in the three configuration files (included)
* Simulation output was analyzed by creating analyzing the console output of the tool and producing plots in python. 

### Results:
The image below shows the egde nodes and the count of devices (on the grid) in time. 
![movie](https://user-images.githubusercontent.com/20401990/135003002-33d4d82f-4faa-43dc-95f2-37291061580e.gif)

These data points (describe the mobility of users deterministically) were inputted into a modified Mobility Model in the EdgeCloudSim to obtain the following results:

Avg_Service_time | Network_Delay
------------ | -------------
![Avg_Service_time](https://user-images.githubusercontent.com/20401990/135003265-5669cc22-fa63-4e3f-b0df-74f78a3eb6b2.png) | ![Network_Delay](https://user-images.githubusercontent.com/20401990/135003277-3a7614ba-98f1-46b2-9573-cfa9d6b0e5fe.png)

While having a higher network delay, the Two_Tier_With_EO offers an average service time less than of the Single_Tier scenario.



Completed_Tasks | Failed_Tasks
------------ | -------------
![Completed_Tasks](https://user-images.githubusercontent.com/20401990/135003266-5fdab4e6-2963-42ca-9aa8-9d556048dcb0.png) |![Failed_Tasks](https://user-images.githubusercontent.com/20401990/135003274-962bd108-9137-4297-9582-88ed3c811ffb.png)

The Two_Tier_With_EO offers a higher percent of completed tasks with lower percent of failed tasks.  


Failed_Tasks_VM_Capacity | Server_Utilization
------------ | -------------
![Failed_Tasks_VM_Capacity](https://user-images.githubusercontent.com/20401990/135003272-773d262e-d8b4-46b7-9edb-47a69561ece0.png) | ![ServerUtilization](https://user-images.githubusercontent.com/20401990/135003279-854b278c-8110-4db1-ada5-2e6d4518fd57.png)

The Two_Tier_With_EO utilizes all VMs (leveraging the benefits of load balancing). Failures in the Single_Tier point towards not enough resources (VMs). Dynamic VM provisioning of new edge nodes and/or VMs on existing edge nodes and/or leveraging mist computing mechanism are potential courses of action in the Single_Tier model.

Failed_MAN      | Failed_Mobility | Failed_Network | Failed_WLAN_Range| Failed_WAN | Failed_WLAN
------------ | ------------- | ------------ | ------------- | ------------ | ------------- |
![Failed_MAN](https://user-images.githubusercontent.com/20401990/135003267-607797da-cb82-48e0-a633-c9b86c696dd6.png) | ![Failed_Tasks_Mobility](https://user-images.githubusercontent.com/20401990/135003268-3fb7c7b1-7501-4aaa-b5c3-9d9eb2aaa132.png) | ![Failed_Tasks_Network](https://user-images.githubusercontent.com/20401990/135003269-09e8bda9-b02f-45cb-988e-b077cb493b03.png) | ![Failed_Tasks_WLAN_RANGE](https://user-images.githubusercontent.com/20401990/135003273-efae7759-587d-4816-9ca3-ac51b43120d2.png) | ![Failed_WAN](https://user-images.githubusercontent.com/20401990/135003275-be67f4cb-49fc-49f8-bc65-18a4afcfaa78.png) | ![Failed_WLAN](https://user-images.githubusercontent.com/20401990/135003276-52609bdf-10ee-4ff8-9ede-bcc597653fac.png)


### To Obtain the Results:
1) Use the pipeline.py to produce the input to the simulation tool;
2) Simulate the environment with the parameters provided in the configuration files.

