// Copyright 1998-2017 Epic Games, Inc. All Rights Reserved.

#include "UE4GoogleAssistant.h"
#include "UE4GoogleAssistantGameMode.h"
#include "UE4GoogleAssistantCharacter.h"

AUE4GoogleAssistantGameMode::AUE4GoogleAssistantGameMode()
{
	// set default pawn class to our Blueprinted character
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnBPClass(TEXT("/Game/ThirdPersonCPP/Blueprints/ThirdPersonCharacter"));
	if (PlayerPawnBPClass.Class != NULL)
	{
		DefaultPawnClass = PlayerPawnBPClass.Class;
	}
}
