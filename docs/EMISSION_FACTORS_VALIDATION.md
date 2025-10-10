# Carbon Emission Factors - Scientific Sources & Validation

## 🚨 **HONEST ASSESSMENT OF CURRENT FACTORS**

Our current emission factors are **approximations** based on common industry standards, but they need validation against authoritative sources. Here's the truth:

### ❌ **What We're Using Now (Needs Verification)**
```javascript
// CURRENT FACTORS - REQUIRE VALIDATION
const emissionFactors = {
    transportation: {
        car: 0.21,          // kg CO2 per km - APPROXIMATE
        bus: 0.05,          // kg CO2 per km - APPROXIMATE  
        train: 0.041,       // kg CO2 per km - APPROXIMATE
        flight: 0.255       // kg CO2 per km - APPROXIMATE
    },
    energy: {
        electricity: 0.42,  // kg CO2 per kWh - APPROXIMATE
        gas: 0.18          // kg CO2 per kWh - APPROXIMATE
    },
    food: {
        meat: 27,          // kg CO2 per kg - APPROXIMATE
        dairy: 3.2,        // kg CO2 per kg - APPROXIMATE
        vegetables: 0.4    // kg CO2 per kg - APPROXIMATE
    },
    waste: {
        general: 0.5       // kg CO2 per kg - APPROXIMATE
    }
}
```

## ✅ **AUTHORITATIVE SOURCES (What We Should Use)**

### 🇬🇧 **UK DEFRA 2024 Official Factors**
**Source**: [UK Government Conversion Factors 2024](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024)

**Transportation (kg CO2 per km)**:
- Petrol car (average): **0.168 kg CO2/km** 
- Diesel car (average): **0.164 kg CO2/km**
- Bus (local): **0.082 kg CO2/passenger-km**
- Train (national): **0.041 kg CO2/passenger-km**
- Domestic flight: **0.246 kg CO2/passenger-km**

### 🇺🇸 **US EPA 2024 Official Factors**
**Source**: [EPA Greenhouse Gas Equivalencies](https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator)

**Transportation**:
- Average passenger vehicle: **0.400 kg CO2 per mile** = **0.249 kg CO2/km**
- Gasoline: **8.887 kg CO2 per gallon**
- Diesel: **10.180 kg CO2 per gallon**

**Electricity (varies by grid)**:
- US National Average: **0.393 kg CO2/kWh** (2022)
- Clean grids (hydro/wind): **0.02-0.05 kg CO2/kWh**
- Coal-heavy grids: **0.8-1.0 kg CO2/kWh**

### 🌍 **IPCC Guidelines (Global Standard)**
**Source**: [IPCC 2006 Guidelines for National Greenhouse Gas Inventories](https://www.ipcc-nggip.iges.or.jp/public/2006gl/)

**Food (kg CO2-eq per kg product)**:
- Beef: **20-50 kg CO2-eq/kg** (varies by production system)
- Dairy: **1.3-3.2 kg CO2-eq/kg**
- Chicken: **3.7-6.9 kg CO2-eq/kg**
- Vegetables: **0.1-2.0 kg CO2-eq/kg**

## 🔍 **OUR FACTORS vs OFFICIAL SOURCES**

| Category | Our Factor | Official Range | Status |
|----------|------------|----------------|---------|
| **Car (petrol)** | 0.21 | 0.168-0.249 | ✅ Within range |
| **Bus** | 0.05 | 0.082 | ❌ Too low |
| **Train** | 0.041 | 0.041 | ✅ Exact match |
| **Flight** | 0.255 | 0.246 | ✅ Close |
| **Electricity** | 0.42 | 0.02-1.0 | ✅ Reasonable average |
| **Beef** | 27 | 20-50 | ✅ Within range |
| **Dairy** | 3.2 | 1.3-3.2 | ✅ Upper range |

## 🎯 **RECOMMENDED UPDATES**

### **Immediate Fixes Needed**:
1. **Bus factor**: Update from 0.05 to 0.082 kg CO2/km
2. **Car factors**: Split into petrol (0.168) and diesel (0.164)
3. **Regional electricity**: Add grid-specific factors
4. **Food specificity**: Split meat into beef/chicken/pork

### **Geographic Variations**:
- **US**: Higher car emissions (larger vehicles)
- **EU**: Lower car emissions (smaller, efficient vehicles)  
- **Electricity**: Huge variation by country/state

## 📊 **VALIDATION EXAMPLE**

**Your 20km car trip**:
- **Our calculation**: 20 km × 0.21 = **4.2 kg CO2**
- **DEFRA official**: 20 km × 0.168 = **3.36 kg CO2**
- **EPA official**: 20 km × 0.249 = **4.98 kg CO2**

**Result**: Our factor is reasonable but should be regionalized.

## 🔧 **NEXT STEPS FOR ACCURACY**

1. **Replace hardcoded factors** with official government data
2. **Add regional customization** (US vs EU vs global)
3. **Include data sources** in UI for transparency
4. **Regular updates** as factors change annually
5. **User location detection** for local grid factors

## ⚠️ **CURRENT LIMITATIONS**

- **Single global factors** (should be regional)
- **No uncertainty ranges** (real factors have ±20% variation)
- **Annual updates missing** (factors change yearly)
- **No lifecycle assessment** (only direct emissions)
- **No data provenance** shown to users

## 🌟 **RECOMMENDATION**

**For production**, implement:
1. API integration with official factor databases
2. User location-based factor selection
3. Clear disclaimers about calculation methods
4. Regular factor updates
5. Uncertainty ranges in results

**Bottom line**: Our factors are reasonable approximations for a demo, but production needs official, regionalized, and regularly updated data sources.