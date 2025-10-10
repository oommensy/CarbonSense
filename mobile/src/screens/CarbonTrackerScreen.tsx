import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  FlatList,
} from 'react-native';

interface CarbonEntry {
  id: string;
  category: string;
  activity: string;
  amount: number;
  unit: string;
  carbonFootprint: number;
  date: Date;
}

interface ActivityOption {
  name: string;
  carbonFactor: number; // kg CO2 per unit
  unit: string;
}

const CATEGORIES = {
  transport: {
    name: 'Transportation',
    icon: '🚗',
    activities: [
      { name: 'Car (Gasoline)', carbonFactor: 0.21, unit: 'km' },
      { name: 'Car (Electric)', carbonFactor: 0.05, unit: 'km' },
      { name: 'Bus', carbonFactor: 0.089, unit: 'km' },
      { name: 'Train', carbonFactor: 0.041, unit: 'km' },
      { name: 'Flight (Domestic)', carbonFactor: 0.255, unit: 'km' },
      { name: 'Flight (International)', carbonFactor: 0.298, unit: 'km' },
      { name: 'Bicycle', carbonFactor: 0, unit: 'km' },
      { name: 'Walking', carbonFactor: 0, unit: 'km' },
    ] as ActivityOption[],
  },
  energy: {
    name: 'Energy',
    icon: '⚡',
    activities: [
      { name: 'Electricity', carbonFactor: 0.5, unit: 'kWh' },
      { name: 'Natural Gas', carbonFactor: 2.04, unit: 'm³' },
      { name: 'Heating Oil', carbonFactor: 2.52, unit: 'L' },
      { name: 'Solar Energy', carbonFactor: 0.046, unit: 'kWh' },
    ] as ActivityOption[],
  },
  food: {
    name: 'Food',
    icon: '🍽️',
    activities: [
      { name: 'Beef', carbonFactor: 27, unit: 'kg' },
      { name: 'Pork', carbonFactor: 12.1, unit: 'kg' },
      { name: 'Chicken', carbonFactor: 6.9, unit: 'kg' },
      { name: 'Fish', carbonFactor: 6.1, unit: 'kg' },
      { name: 'Vegetables', carbonFactor: 2.0, unit: 'kg' },
      { name: 'Fruits', carbonFactor: 1.1, unit: 'kg' },
      { name: 'Dairy', carbonFactor: 3.2, unit: 'kg' },
      { name: 'Grains', carbonFactor: 1.4, unit: 'kg' },
    ] as ActivityOption[],
  },
  waste: {
    name: 'Waste',
    icon: '🗑️',
    activities: [
      { name: 'Landfill Waste', carbonFactor: 0.57, unit: 'kg' },
      { name: 'Recycling', carbonFactor: 0.1, unit: 'kg' },
      { name: 'Composting', carbonFactor: 0.05, unit: 'kg' },
    ] as ActivityOption[],
  },
};

const CarbonTrackerScreen = () => {
  const [entries, setEntries] = useState<CarbonEntry[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedActivity, setSelectedActivity] = useState<ActivityOption | null>(null);
  const [amount, setAmount] = useState('');

  const addEntry = () => {
    if (!selectedActivity || !amount || parseFloat(amount) <= 0) {
      Alert.alert('Error', 'Please select an activity and enter a valid amount');
      return;
    }

    const carbonFootprint = selectedActivity.carbonFactor * parseFloat(amount);
    const newEntry: CarbonEntry = {
      id: Date.now().toString(),
      category: selectedCategory,
      activity: selectedActivity.name,
      amount: parseFloat(amount),
      unit: selectedActivity.unit,
      carbonFootprint: Math.round(carbonFootprint * 100) / 100,
      date: new Date(),
    };

    setEntries([newEntry, ...entries]);
    setModalVisible(false);
    setSelectedCategory('');
    setSelectedActivity(null);
    setAmount('');
    
    Alert.alert(
      'Entry Added',
      `Added ${carbonFootprint.toFixed(2)} kg CO2 from ${selectedActivity.name}`,
      [{ text: 'OK' }]
    );
  };

  const getTotalCarbonToday = () => {
    const today = new Date().toDateString();
    return entries
      .filter(entry => entry.date.toDateString() === today)
      .reduce((total, entry) => total + entry.carbonFootprint, 0)
      .toFixed(2);
  };

  const deleteEntry = (id: string) => {
    Alert.alert(
      'Delete Entry',
      'Are you sure you want to delete this entry?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => {
          setEntries(entries.filter(entry => entry.id !== id));
        }},
      ]
    );
  };

  const renderCategorySelection = () => (
    <View style={styles.categoryGrid}>
      {Object.entries(CATEGORIES).map(([key, category]) => (
        <TouchableOpacity
          key={key}
          style={styles.categoryButton}
          onPress={() => setSelectedCategory(key)}
        >
          <Text style={styles.categoryIcon}>{category.icon}</Text>
          <Text style={styles.categoryName}>{category.name}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderActivitySelection = () => (
    <View>
      <Text style={styles.modalTitle}>
        Select Activity - {CATEGORIES[selectedCategory as keyof typeof CATEGORIES]?.name}
      </Text>
      <FlatList
        data={CATEGORIES[selectedCategory as keyof typeof CATEGORIES]?.activities || []}
        keyExtractor={(item) => item.name}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.activityButton,
              selectedActivity?.name === item.name && styles.selectedActivity
            ]}
            onPress={() => setSelectedActivity(item)}
          >
            <Text style={styles.activityName}>{item.name}</Text>
            <Text style={styles.activityUnit}>per {item.unit}</Text>
            <Text style={styles.carbonFactor}>
              {item.carbonFactor} kg CO2/{item.unit}
            </Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );

  const renderAmountInput = () => (
    <View>
      <Text style={styles.inputLabel}>
        Amount ({selectedActivity?.unit})
      </Text>
      <TextInput
        style={styles.amountInput}
        value={amount}
        onChangeText={setAmount}
        placeholder={`Enter amount in ${selectedActivity?.unit}`}
        keyboardType="numeric"
      />
      {selectedActivity && amount && parseFloat(amount) > 0 && (
        <Text style={styles.carbonPreview}>
          Carbon footprint: {(selectedActivity.carbonFactor * parseFloat(amount)).toFixed(2)} kg CO2
        </Text>
      )}
    </View>
  );

  const renderEntry = ({ item }: { item: CarbonEntry }) => (
    <View style={styles.entryCard}>
      <View style={styles.entryHeader}>
        <Text style={styles.entryActivity}>{item.activity}</Text>
        <TouchableOpacity
          onPress={() => deleteEntry(item.id)}
          style={styles.deleteButton}
        >
          <Text style={styles.deleteButtonText}>✕</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.entryDetails}>
        {item.amount} {item.unit} • {item.carbonFootprint} kg CO2
      </Text>
      <Text style={styles.entryDate}>
        {item.date.toLocaleDateString()} at {item.date.toLocaleTimeString()}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Carbon Tracker</Text>
        <Text style={styles.subtitle}>Track your daily carbon footprint</Text>
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Today's Carbon Footprint</Text>
        <Text style={styles.summaryValue}>{getTotalCarbonToday()} kg CO2</Text>
        <Text style={styles.summarySubtext}>
          {entries.filter(e => e.date.toDateString() === new Date().toDateString()).length} entries today
        </Text>
      </View>

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => setModalVisible(true)}
      >
        <Text style={styles.addButtonText}>+ Add Carbon Entry</Text>
      </TouchableOpacity>

      <FlatList
        data={entries}
        keyExtractor={(item) => item.id}
        renderItem={renderEntry}
        contentContainerStyle={styles.entriesList}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>No entries yet</Text>
            <Text style={styles.emptySubtext}>
              Start tracking your carbon footprint by adding your first entry
            </Text>
          </View>
        }
      />

      <Modal
        visible={modalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity
              onPress={() => {
                setModalVisible(false);
                setSelectedCategory('');
                setSelectedActivity(null);
                setAmount('');
              }}
            >
              <Text style={styles.cancelButton}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalHeaderTitle}>Add Entry</Text>
            <TouchableOpacity
              onPress={addEntry}
              disabled={!selectedActivity || !amount}
              style={[
                styles.addModalButton,
                (!selectedActivity || !amount) && styles.disabledButton
              ]}
            >
              <Text style={[
                styles.addModalButtonText,
                (!selectedActivity || !amount) && styles.disabledButtonText
              ]}>Add</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            {!selectedCategory && renderCategorySelection()}
            {selectedCategory && !selectedActivity && renderActivitySelection()}
            {selectedActivity && renderAmountInput()}
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#2E7D32',
    paddingTop: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  summaryCard: {
    backgroundColor: 'white',
    margin: 15,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  summaryTitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  summaryValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 5,
  },
  summarySubtext: {
    fontSize: 14,
    color: '#999',
  },
  addButton: {
    backgroundColor: '#2E7D32',
    marginHorizontal: 15,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  addButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  entriesList: {
    paddingHorizontal: 15,
  },
  entryCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  entryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  entryActivity: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  deleteButton: {
    padding: 5,
  },
  deleteButtonText: {
    color: '#ff4444',
    fontSize: 16,
    fontWeight: 'bold',
  },
  entryDetails: {
    fontSize: 14,
    color: '#666',
    marginBottom: 3,
  },
  entryDate: {
    fontSize: 12,
    color: '#999',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 50,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  cancelButton: {
    color: '#666',
    fontSize: 16,
  },
  modalHeaderTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  addModalButton: {
    backgroundColor: '#2E7D32',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 6,
  },
  addModalButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '500',
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  disabledButtonText: {
    color: '#999',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  categoryButton: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  categoryIcon: {
    fontSize: 32,
    marginBottom: 10,
  },
  categoryName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    textAlign: 'center',
  },
  activityButton: {
    padding: 15,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    marginBottom: 10,
    backgroundColor: 'white',
  },
  selectedActivity: {
    borderColor: '#2E7D32',
    backgroundColor: '#f1f8e9',
  },
  activityName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 3,
  },
  activityUnit: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  carbonFactor: {
    fontSize: 12,
    color: '#2E7D32',
    fontWeight: '500',
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 10,
    marginTop: 20,
  },
  amountInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    backgroundColor: 'white',
  },
  carbonPreview: {
    marginTop: 10,
    padding: 15,
    backgroundColor: '#f1f8e9',
    borderRadius: 8,
    fontSize: 16,
    color: '#2E7D32',
    fontWeight: '500',
    textAlign: 'center',
  },
});

export default CarbonTrackerScreen;