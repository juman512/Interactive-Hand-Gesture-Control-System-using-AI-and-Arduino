int leds[] = {6, 5, 11, 9, 7};

int buzzer = 4;

// نغمات الأصابع
int notes[] = {
  262,  // Thumb
  330,  // Index
  392,  // Middle
  440,  // Ring
  523   // Pinky
};

void setup() {

  // إعداد الـ LEDs
  for (int i = 0; i < 5; i++) {

    pinMode(leds[i], OUTPUT);

    digitalWrite(leds[i], LOW);
  }

  // إعداد البازر
  pinMode(buzzer, OUTPUT);

  noTone(buzzer);

  // Serial
  Serial.begin(9600);
}


void loop() {

  if (Serial.available()) {

    String data = Serial.readStringUntil('\n');

    // لازم تكون البيانات 5 أرقام
    // مثال: 10100
    if (data.length() == 5) {

      // تشغيل وإطفاء الـ LEDs
      for (int i = 0; i < 5; i++) {

        if (data[i] == '1') {

          digitalWrite(leds[i], HIGH);

        } else {

          digitalWrite(leds[i], LOW);
        }
      }


      // تشغيل نغمة الإصبع المرفوع
      bool fingerFound = false;

      for (int i = 0; i < 5; i++) {

        if (data[i] == '1') {

          tone(buzzer, notes[i]);

          fingerFound = true;

          break;
        }
      }


      // إذا ما في أي إصبع مرفوع
      if (!fingerFound) {

        noTone(buzzer);
      }
    }
  }
}
