# Development Team Project: Suspect Sources System for the Dutch National Cyber Security Centre

## Table of Contents
1. [Project Introduction](#introduction)
2. [Vulnerabilities and Mitigations](#vulnerabilities-and-mitigations)
3. [Security Requirements](#security-requirements)
4. [Implementation Challenges](#implementation-challenges)
5. [Conclusion](#conclusion)
6. [Appendix A: Vulnerability Risk Assessment](#appendix-a:-vulnerability-risk-assessment)
7. [Appendix B: System Architecture](#appendix-b)
8. [Appendix C: Execution Instructions via Docker](#appendix-c)
9. [Appendix D: Testing and Quality Assurance](#appendix-d)


## Project Introduction
The goal of this project is to implement a system prototype for a Smart Home system integrating the security requirements identified on the Attack-Defence Tree analysis previously performed.

The prototype is composed of one client device that manages several thermostat controller nodes. The MQTT (Message Queuing Telemetry Transport) message broker has been used to manage communication between nodes. The MQTT has become the standard protocol for the Internet of Things (IoT) due to its simple and lightweight clients that require minimal resources (Yuan, 2021). 
MQTT aims to be a protocol for resource-constrained devices and low-bandwidth, high-latency, unreliable networks (MQTT, 2021). 

Furthermore, MQTT includes security features such as data in transit encryption using TLS and strong client authentication that cover most of the security requirements found in our analysis. 

The prototype has been developed based on the following SysML diagrams:

![SysML Requirements](https://i.imgur.com/LL4Sf53.png)

![SysML Security Requirements](https://i.imgur.com/gQhlphz.png)

![Sequence Diagramm MQTT Authentication](https://i.imgur.com/la9EZ3i.png)

## Vulnerabilities and Mitigations
The vulnerability analysis presented in the Design Document has been extended to include a quantitative assessment based on likelihood and impact scales allowing us to create a raking and prioritize the implementation of the mitigation measures ([Appendix A: Vulnerability Risk Assessment](#appendix-a:-vulnerability-risk-assessment)). 

In addition to our analysis, the OWASP top 10 vulnerabilities of IoT (OWASP, 2018) were considered when identifying security controls.

## Security Requirements
These are the Security Controls that have been implemented in the prototype: 
* The encryption of data in transit has been implemented by enabling TLS certificates on the MQTT broker side.
* Authentication of devices before receiving and transmitting data done with username and password.
* To implement the secure boot feature or verification of code signatures, an RSA public/private key pair has been created and the private key has been used to sign the files.  The signatures for the device and controller python files are stored in the respective config folders. Upon execution of the code, the source code is checked against its signature to ensure that the file has not been tampered with.
* All connections with the MQTT broker have been audited through a topic and are stored locally on the Broker. The purpose of this audit log is to serve as input data for a monitoring and analysis tool or Intrusion Detection System (IDS).
* Ports have been whitelisted at broker level to reduce the IP range that is allowed to connect to the broker minimizing the probability of a Denial of Service (DoS) attack.
* The principle of least privilege has been configured in the broker.
* Protection of user credentials has been implemented by using symmetric encryption keys to generate and validate credentials.


## Implementation Challenges
Docker containers have been used in the prototype to configure light virtual machine containers in order to simulate a distributed system (Docker, N.D.). 

Common distributed system challenges include latency and message loss, our prototype also has IoT limitations like bandwidth and processing power (Gerber & Romeo, 2020). The table below demonstrates what measures MQTT has taken to lessen these challenges:

![IoT Challenges](https://i.imgur.com/Ld7sZT0.png)
*Figure 4: Challenges in IoT and Mitigations offered by MQTT.*

## Conclusion
Due to the time constrain of the project, during the prototype development we have concentrated our efforts on the implementation of the security requirements and therefore, some of the functional requirements like the temperature control have been omitted. 

Security features for future work include access control mechanism, monitoring and analysis tools and device security updates management.


## APPENDIX A: Vulnerability Risk Assessment
The main goal of this assessment is to assign a risk score to each vulnerability identified in the AD Tree analysis based on the technical capability needed to exploit the vulnerability (Likelihood) and the damage caused by the exploit (Impact) (Sutton, 2014). 

The following table includes list of vulnerabilities found and the risk evaluation along with the mitigations identified for each vulnerability: 

![Vulnerability Impact and Liklihood](https://i.imgur.com/8gyt44r.png)
*Figure 5: Vulnerabilities and their Impact and Liklihood.*

![Risk Definition](https://i.imgur.com/eEYj0JL.png)
*Figure 6: Risk Definition.*

## APPENDIX B: System Architecture
TBA

## APPENDIX C: Execution Instructions via Docker
To make the execution as seamless as possible, we created Dockerfiles for both the Client Device and the Controller. This allows for building Docker Images for both and launching one or more of each as seperate Container Instances.

Docker is an open-source project that automates the deployment of applications inside software containers, by providing an additional layer of abstraction and automation of operating-system-level virtualization on Linux, Mac OS and Windows.

We have included the .tar archives of the docker images directly in the Repo, which can be loaded using the command:

`$ docker import file [REPOSITORY[:TAG]]`

Documentation: https://docs.docker.com/engine/reference/commandline/import/

Once the images are present in your Docker, you will be able to run a new container using the images. To do so, please ensure that you run the container in interactive mode, to be able to interact with the python user inputs:

`$ docker run -it [REPOSITORY[:TAG]]`

Documentation: https://docs.docker.com/engine/reference/commandline/run/

When importing the images you can set a repository name and tag, which you will need to reference in the run command. One example for naming conventions could for instance be:
```
ssa-project:controller
ssa-project:device
```

By running the “run” command multiple times on the same image, you can spin up multiple containers for the same category. This makes sense for when you want to test multiple devices running on the same network and all communicating with a single controller.

## APPENDIX D: Testing and Quality Assurance
Throughout the project, three levels of testing were utilised to ensure quality and functional integrity of the system:
- **Unit Testing**
- **Continuous Review via Linters**
- **Functional Test Plan (End-to-End)**

A unit test is a way of testing a unit - the smallest piece of code that can be logically isolated in a system. In most programming languages, that is a function, a subroutine, a method or property. In the Smart Home System, this would mean the outputs of the various functions are tested to confirm that they fulfill expectations in terms of typing and values. Ideally, for the complete system implementation, a framework such as "unittest" or "Robot" could be used to create automated test cases that verify the outputs on-demand. 
For instance, whenever a major code update is pushed, the unit tests could then be run before merging the code to confirm that previous functions are not affected by the update.

In the case of the proof of concept implementation, we have instead opted to go with print-based unit tests due to the tight timeline. While developing and adjusting code, print statements were used to verify the outputs of functions and ensure that the individual units of the System are working as expected.

Continuous Source Code review is done to ensure the structure, style, complexity, syntax, and security aspect of the source code as a whole is guaranteed. This can be done with the help of static code analysis tools called Linters. For this project, we decided to go with two different Linters to cover most bases:
**Pylint** for checking the syntax, complexity, styling and referencing of the code basis.
**Bandit** for checking security due to its capability of flagging vulnerabilities and their severeness.

By following the Pylint feedback, we quickly raised our initial code score from around 6 to 9+ / 10 points for both the client and device modules. The only remaining issue were unused arguments which were set by the on_connect() function from Paho MQTT and our Thermometer device class being very slim (only PoC) and thus having too few public methods to call.

![Pylint Final Score for Source Code](https://i.imgur.com/8EnPo1H.png)
*Figure 7: Pylint Final Score for Device Source Code*

![Pylint Final Score for Source Code](https://i.imgur.com/NhUp0CB.png)
*Figure 8: Pylint Final Score for Controller Source Code*


Bandit flagged one remaining low severity security issue namely that we using a pseudo-random generator for our device temperature allocation with the random.uniform() function, and that this is not suitable for security/cryptographic purposes. However, we only use the uniform function to allocate random temperatures to our thermometer devices as test data and therefore using pseudo-random number generators are fine. Other than that no issues were flagged.

![Bandit's Final Run with No Issues Found](https://i.imgur.com/QeE8BrV.png)
*Figure 9: Bandit's Final Run with No Issues Found.*

The last type of testing was done before submitting the final project. Functional Testing ensures that all end-to-end use cases and user scenarios that will be done via the System are included and working. First, we established a Functional Test Plan containing a full checklist of test cases for the individual roles and the System in general. We then proceeded with manually testing each of the test scenarios to ensure that the System as a whole is working as per the use-case specifications. The complete Functional Test Plan can be found below. Doing so gave certainty that all use cases the System set out to cater towards were fulfilled.

The full end-to-end Functional Test Plan can be found here: [Functional Test Plan](https://github.com/MarzioHr/SSA_Project/blob/main/Functional%20Test%20Plan.pdf)


## Reference List
Berstein, C., Brush, K. & Gillis, A. (2021) MQTT (MQ Telemetry Transport) Definition. Available from: https://internetofthingsagenda.techtarget.com/definition/MQTT-MQ-Telemetry-Transport [Accessed 5 March 2022]

Docker (N.D.) Use containers to Build, Share and Run your applications. Available from: https://www.docker.com/resources/what-container [Accessed 28 February 2022]

Gerber, A. & Romeo, J. (2020) Connecting all the things in the Internet of Things. https://developer.ibm.com/articles/iot-lp101-connectivity-network-protocols/ [Accessed 26 February 2022]

Liu, Y. & Al-Masri, E. (2021) Evaluating the Reliability of MQTT with Comparative Analysis. IEEE 4th International Conference on Knowledge Innovation and Invention (ICKII) 2021: 24-29. Available from: https://ieeexplore.ieee.org/document/9574783 [Accessed 3 March 2022]

MQTT (N.D) MQTT - The Standard for IoT Messaging. Available from: https://mqtt.org/ [Accessed 5 March 2022]

OWASP (2018) OWASP Top 10 Internet of Things. Available from: https://owasp.org/www-pdf-archive/OWASP-IoT-Top-10-2018-final.pdf [Accessed 28 February 2022]

Sutton, D. (2014) Information Risk Management. 2nd ed. Swindon, UK: BCS Learning & Development Limited. 
The HiveMQ Team (2015) Quality of Service 0,1 & 2 - MQTT Essentials: Part 6. Available from: https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/ [Accessed 27 February 2022]

Tracy, P (2016) MQTT protocol minimizes network bandwidth for the internet of things. Available from: https://www.rcrwireless.com/20161129/fundamentals/mqtt-internet-of-things-tag31-tag99 [Accessed 26 February 2022]

Yuan, M (2021) Getting to know MQTT. Available from: https://developer.ibm.com/articles/iot-mqtt-why-good-for-iot/ [Accessed 4 March 2022]
Wang, C (2018) HTTP vs. MQTT: A tale of two IoT protocols. Available from:  https://cloud.google.com/blog/products/iot-devices/http-vs-mqtt-a-tale-of-two-iot-protocols [Accessed 26 February 2022]