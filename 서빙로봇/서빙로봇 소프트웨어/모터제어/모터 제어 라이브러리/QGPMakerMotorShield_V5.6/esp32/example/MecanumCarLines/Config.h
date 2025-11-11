/*
Name:		Config.h
Version:	1.0.0
Created:	
Author:		Lien
Github:		
Copyright (c) 2017 Evert Arias
*/

#pragma once

#ifndef _Config_h
#define _Config_h

#define  VERSION        1

//EasyBuzzer
#define DEFAULT_PIN			A3		// Default pin number where the buzzer is connected.	
#define DEFAULT_FREQ		1000    // Default frequency.
#define DEFAULT_CHANNEL		0		// Default PWM channel.
#define DEFAULT_RESOLUTION	8		// Default resolution.
#define MINIMUM_INTERVAL    20      // Minimum interval allowed in milliseconds(ms).

#define DEFAULT_ON_DURATION		100 // Default ON duration of a cycle in milliseconds(ms).
#define DEFAULT_OFF_DURATION	100 // Default OFF duration of a cycle in milliseconds(ms).
#define DEFAULT_PAUSE_DURATION	100 // Default PAUSE duration of a cycle in milliseconds(ms).

#define UART_NUMBER 1

#endif
