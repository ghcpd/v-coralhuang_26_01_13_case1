#!/usr/bin/env python3
import statistics

from fake import UserAgent
from utils import load


def main():
    data = load()
    print(f"Total UAs: {len(data)}")
    ua = UserAgent()
    samples = [ua.random for _ in range(1000)]
    unique = len(set(samples))
    repetition_rate = (1000 - unique) / 1000 * 100
    print(f"Generated: 1000 samples")
    print(f"Unique: {unique} different UAs")
    print(f"Repetition rate: {repetition_rate:.1f}%")


if __name__ == '__main__':
    main()
