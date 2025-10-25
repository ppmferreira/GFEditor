# Classes

## Classes Guerreiras

    'Lutador': 1,
    'Guerreiro': 2,
    'Berzerker': 3,
    'Paladino': 4,
    'Titan': 17,
    'Templario': 18,
    'Cavaleiro da Morte': 32,
    'Cavaleiro Real': 33,
    'Destruidor': 40,
    'Cavaleiro Sagrado': 41,

## Classes Arqueiras

    'Caçador': 5,
    'Arqueiro': 6,
    'Ranger': 7,
    'Assassin': 8,
    'Franco Atirador': 19,
    'Sicario Sombrio': 20,
    'Mercenario': 34,
    'Ninja': 35,
    'Predador': 42,
    'Shinobi': 43,

## Classes Sacerdotes

    'Acolito': 9,
    'Sacerdote': 10,
    'Clerigo': 11,
    'Sabio': 12,
    'Profeta': 21,
    'Mistico': 22,
    'Mensageiro Divino': 36,
    'Xamã': 37,
    'Arcanjo': 44,
    'Druida': 45,

## Classes Mágicas

    'Bruxo': 13,
    'Mago': 14,
    'Feiticeiro': 15,
    'Necromante': 16,
    'Arquimago': 23,
    'Demonologo': 24,
    'Arcano': 38,
    'Emissario dos Mortos': 39,
    'Shinigami': 47,

## Classes Maquinista

    'Maquinista Aprendiz': 25,
    'Maquinista': 26,
    'Agressor': 27,
    'Demolidor': 28,
    'Prime': 29,
    'Optimus': 30,
    'Megatron': 48,
    'Galvatron': 49,
    'Omega': 50,
    'Titan Celeste': 51,

## Classes Viajante

    'Viajante': 52,
    'Nomade': 53,
    'Espadachim': 54,
    'Ilusionista': 55,
    'Samurai': 56,
    'Augure': 57,
    'Ronin': 58,
    'Oraculo': 59,
    'Mestre Dimensional': 60,
    'Cronos': 61,

# Documentação

## Pipes Order

``Id,  IconFilename,  ModelId,  ModelFilename,  WeaponEffectId,  FlyEffectId,  UsedEffectId,  UsedSoundName,  EnhanceEffectId,  Name,  ItemType,  EquipType,  OpFlags,  OpFlagsPlus,  Target,  RestrictGender,  RestrictLevel,  RestrictMaxLevel,  RebirthCount,  RebirthScore,  RebirthMaxScore,  RestrictAlign,  RestrictPrestige,  RestrictClass,  ItemQuality,  ItemGroup,  CastingTime,  CoolDownTime,  CoolDownGroup,  MaxHp,  MaxMp,  Str,  Vit,  Int,  Von,  Agi,  AvgPhysicoDamage,  RandPhysicoDamage,  AttackRange,  AttackSpeed,  Attack,  RangeAttack,  PhysicoDefence,  MagicDamage,  MagicDefence,  HitRate,  DodgeRate,  PhysicoCriticalRate,  PhysicoCriticalDamage,  MagicCriticalRate,  MagicCriticalDamage,  PhysicalPenetration,  MagicalPenetration,  PhysicalPenetrationDefence,  MagicalPenetrationDefence,  Attribute,  AttributeRate,  AttributeDamage,  AttributeResist,  SpecialType,  SpecialRate,  SpecialDamage,  DropRate,  DropIndex,  TreasureBuffs,  TreasureBuffs,  TreasureBuffs,  TreasureBuffs,  EnchantType,  EnchantId,  ExpertLevel,  ExpertEnchantId,  ElfSkillId,  EnchantTimeType,  EnchantDuration,  LimitType,  DueDateTime,  BackpackSize,  MaxSocket,  SocketRate,  MaxDurability,  MaxStack,  ShopPriceType,  SysPrice,  RestrictEventPosId,  MissionPosId,  BlockRate,  LogLevel,  AuctionType,  ExtraData,  ExtraData,  ExtraData,  Tip``

## **Flags**

```cpp
CanUse             = 1,
NoDecrease         = 2,
NoTrade            = 4,
NoDiscard          = 8,
OnlyStartBit       = 16,
NoEnhance          = 16, // Duplicated value, might be an error?
ReplaceableStartBit = 21,
NoRepair           = 32,
Combineable        = 64,
BindOnEquip        = 128,
AccumTime          = 256,
NoSameBuff         = 512,
NoInBattle         = 1024,
NoInTown           = 2048,
NoInCave           = 4096,
NoInInstance       = 8192,
LinkToQuest        = 16384,
ForDead            = 32768,
Only1              = 65536,
Only2              = 131072,
Only3              = 262144,
Only4              = 524288,
Only5              = 1048576,
Only               = 2031616,
Replaceable1       = 2097152,
Replaceable2       = 4194304,
Replaceable3       = 8388608,
Replaceable4       = 16777216,
Replaceable5       = 33554432,
Replaceable        = 65011712,
NoInBattlefield    = 67108864,
NoInField          = 134217728,
NoTransNode        = 268435456,
UnBindItem         = 536870912
```

**Flags**

```cpp
CanUse             = 1,
NoDecrease         = 2,
NoTrade            = 4,
NoDiscard          = 8,
OnlyStartBit       = 16,
NoEnhance          = 16, // Duplicated value, might be an error?
ReplaceableStartBit = 21,
NoRepair           = 32,
Combineable        = 64,
BindOnEquip        = 128,
AccumTime          = 256,
NoSameBuff         = 512,
NoInBattle         = 1024,
NoInTown           = 2048,
NoInCave           = 4096,
NoInInstance       = 8192,
LinkToQuest        = 16384,
ForDead            = 32768,
Only1              = 65536,
Only2              = 131072,
Only3              = 262144,
Only4              = 524288,
Only5              = 1048576,
Only               = 2031616,
Replaceable1       = 2097152,
Replaceable2       = 4194304,
Replaceable3       = 8388608,
Replaceable4       = 16777216,
Replaceable5       = 33554432,
Replaceable        = 65011712,
NoInBattlefield    = 67108864,
NoInField          = 134217728,
NoTransNode        = 268435456,
UnBindItem         = 536870912
```

## **OP FlagPLus**

```cpp
IKCombine           = 1,
GKCombine           = 2,
EquipShow           = 4,
PurpleWLimit        = 8,
PurpleALimit        = 16,
UseBind             = 32,
OneStack            = 64,
RideCombineIK       = 128,
RideCombineGK       = 256,
ISRideCombine       = 384, // Note: This value is a sum of the previous two
VIP                 = 512,
ChairCombineIK      = 2048,
ChairCombineGK      = 4096,
ISChairCombine      = 6144, // Note: This value is a sum of the previous two
RedWLimit           = 8192,
RedALimit           = 16384,
CrystalCombo        = 32768,
SouvenirCombo       = 65536,
GodAreaCombo        = 131072,
ElftabletEquip      = 262144,
ElftabletExp        = 524288,
ShowProbability     = 1048576,
StorageForbidden    = 2097152,
FamilyStorageForbidden = 4194304
```

## **ItemQuality**

```cpp
Gray   = 1,
Green  = 2,
Blue   = 3,
Orange = 4,
Yellow = 5,
Purple = 6,
Red    = 7,
End    = 8
```

## **itemTarget**

```c++
None        = 1,
ToSelf      = 2,
ToElf       = 3,
ToChar      = 4,
ToItem      = 5,
ToCrop      = 6,
ToFarm      = 7,
ToIsleScene = 8,
ToIsleStatue= 9,
ToHiredFarm = 10,
ToFishGround= 11,
ToFish      = 12,
ToPit       = 13,
ToMineral   = 14,
ToPlant     = 15,
ToIsleFarm  = 16,
ToCattle    = 17,
ToPasturage = 18,
ToESShortcut= 19,
ToMonster   = 20,
ToNPC       = 21,
ToSpellAA   = 22
```

## **ItemQuality**

```cpp
Gray   = 1,
Green  = 2,
Blue   = 3,
Orange = 4,
Yellow = 5,
Purple = 6,
Red    = 7,
End    = 8
```

## **itemTarget**

```c++
None        = 1,
ToSelf      = 2,
ToElf       = 3,
ToChar      = 4,
ToItem      = 5,
ToCrop      = 6,
ToFarm      = 7,
ToIsleScene = 8,
ToIsleStatue= 9,
ToHiredFarm = 10,
ToFishGround= 11,
ToFish      = 12,
ToPit       = 13,
ToMineral   = 14,
ToPlant     = 15,
ToIsleFarm  = 16,
ToCattle    = 17,
ToPasturage = 18,
ToESShortcut= 19,
ToMonster   = 20,
ToNPC       = 21,
ToSpellAA   = 22
```
